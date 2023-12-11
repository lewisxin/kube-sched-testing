FILE:=transcode-video-tmpl.yaml
CLUSTER:=k8s-multi-node
TEMP_FOLDER=temp
POD_COLUMNS:="NAME:.metadata.name,POD_CREATED:.metadata.creationTimestamp,POD_STARTED:.status.startTime,POD_SCHED:.status.conditions[?(@.type==\"PodScheduled\")].lastTransitionTime,STARTED:.status.containerStatuses[*].state.*.startedAt,FINISHED:.status.containerStatuses[*].state.*.finishedAt,NODE:.spec.nodeName,STATUS:.status.containerStatuses[*].state.*.reason,DDL:.metadata.annotations['rt-preemptive\.scheduling\.x-k8s\.io/ddl'],PRIORITY:.spec.priority"
CURRENT_UNIX=$$(date +%s)
SCHED_IMAGE:=localhost:5000/scheduler-plugins/kube-scheduler:latest
KIND_BASE_IMG:=
PLUGIN:=default

all: generate

helm.install:
	curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3
	chmod 700 get_helm.sh
	./get_helm.sh

cluster.build:
	GOFLAGS='-buildvcs=false' kind build node-image --base-image ${KIND_BASE_IMG}
	
cluster.up:
	kind create cluster --image kindest/node:latest --name $(CLUSTER) --config manifests/kind-conf.yaml
	kind load docker-image $(SCHED_IMAGE) --name $(CLUSTER)
	kubectl get clusterrole system:kube-scheduler -o yaml | yq e '.rules[] |= (with(select(.resources[] | select(. == "pods")); .verbs += "update"))' > manifests/clusterrole-sched.yaml
	kubectl apply -f manifests/clusterrole-sched.yaml
	rm manifests/clusterrole-sched.yaml
	make cluster.load-image

cluster.load-image:
	kind load docker-image video-transcoding:latest --name $(CLUSTER)

cluster.down:
	kind delete cluster --name $(CLUSTER)

config.edfpreemptivescheduler:
	docker cp manifests/edf-preemptive.yaml $(CLUSTER)-control-plane:/etc/kubernetes/.
	docker cp manifests/kube-scheduler-edf-preemptive.yaml $(CLUSTER)-control-plane:/etc/kubernetes/.
	docker exec $(CLUSTER)-control-plane cp /etc/kubernetes/manifests/kube-scheduler.yaml /etc/kubernetes/kube-scheduler.yaml
	docker exec $(CLUSTER)-control-plane cp /etc/kubernetes/kube-scheduler-edf-preemptive.yaml /etc/kubernetes/manifests/kube-scheduler.yaml

config.llfpreemptivescheduler:
	docker cp manifests/llf-preemptive.yaml $(CLUSTER)-control-plane:/etc/kubernetes/.
	docker cp manifests/kube-scheduler-llf-preemptive.yaml $(CLUSTER)-control-plane:/etc/kubernetes/.
	docker exec $(CLUSTER)-control-plane cp /etc/kubernetes/manifests/kube-scheduler.yaml /etc/kubernetes/kube-scheduler.yaml
	docker exec $(CLUSTER)-control-plane cp /etc/kubernetes/kube-scheduler-llf-preemptive.yaml /etc/kubernetes/manifests/kube-scheduler.yaml

config.disable-noderesources:
	docker cp manifests/disable-noderesources.yaml $(CLUSTER)-control-plane:/etc/kubernetes/.
	docker cp manifests/kube-scheduler-disable-noderesources.yaml $(CLUSTER)-control-plane:/etc/kubernetes/.
	docker exec $(CLUSTER)-control-plane cp /etc/kubernetes/manifests/kube-scheduler.yaml /etc/kubernetes/kube-scheduler.yaml
	docker exec $(CLUSTER)-control-plane cp /etc/kubernetes/kube-scheduler-disable-noderesources.yaml /etc/kubernetes/manifests/kube-scheduler.yaml

config.defaultscheduler:
	docker exec $(CLUSTER)-control-plane cp /etc/kubernetes/kube-scheduler.yaml /etc/kubernetes/manifests/kube-scheduler.yaml

pv.config:
	kubectl apply -f nfs

pv.reload:
	pv_name=$$(kubectl get pv -o custom-columns=NAME:.metadata.name --no-headers); \
	docker exec $(CLUSTER)-worker rm -rf /tmp/nfs-provisioner/$$pv_name/videos; \
	docker exec $(CLUSTER)-worker mkdir -p /tmp/nfs-provisioner/$$pv_name/videos; \
	docker cp apps/video-transcoding/data/. $(CLUSTER)-worker:/mnt; \
	docker exec $(CLUSTER)-worker mv /mnt/trailer1.mp4 /mnt/trailer2.mp4 /mnt/trailer3.mp4 /tmp/nfs-provisioner/$$pv_name/videos

pv.dump:
	mkdir -p temp/dump
	docker cp $(CLUSTER)-worker:/mnt/videos temp/dump/

deploy.prios:
	kubectl apply -f prios

delete.jobs:
	kubectl delete jobs -l jobgroup=video-transcoding
	kubectl delete jobs -l jobgroup=countdown
	kubectl delete pods -l jobgroup=countdown
	kubectl delete pods -l jobgroup=stress

print.pods:
	kubectl get pods -o custom-columns=$(POD_COLUMNS)

plot:
	@mkdir -p $(TEMP_FOLDER) && \
	python graph.py -i pod_events_$(PLUGIN).csv

log:
	@mkdir -p out
	@kubectl get pods -o custom-columns=$(POD_COLUMNS) > out/pod_status_$(CURRENT_UNIX).log
	@kubectl describe pods > out/pod_desc_$(CURRENT_UNIX).log

clean:
	rm -rf jobs $(TEMP_FOLDER)

podlistener.up:
	go build -o ./build/podlistener ./src/eventlistener
	./build/podlistener --plugin=$(PLUGIN)

exp.run:
	go build -o ./build/exp ./src/experiment
	./build/exp -t templates/${FILE} -d data/jobs.csv

image.build:
	docker build -t video-transcoding ./apps/video-transcoding