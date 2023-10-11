FILE:=countdown-ddl-tmpl.yaml
CLUSTER:=k8s-multi-node
TEMP_FOLDER=temp
POD_COLUMNS:="NAME:.metadata.name,POD_CREATED:.metadata.creationTimestamp,POD_STARTED:.status.startTime,POD_SCHED:.status.conditions[?(@.type==\"PodScheduled\")].lastTransitionTime,STARTED:.status.containerStatuses[*].state.*.startedAt,FINISHED:.status.containerStatuses[*].state.*.finishedAt,NODE:.spec.nodeName,STATUS:.status.containerStatuses[*].state.*.reason,DDL:.metadata.annotations['rt-preemptive\.scheduling\.x-k8s\.io/ddl'],PRIORITY:.spec.priority"
CURRENT_UNIX=$$(date +%s)
SCHED_IMAGE:=localhost:5000/scheduler-plugins/kube-scheduler:latest
POD_IMAGE:=centos:7
KIND_BASE_IMG:=

all: generate

cluster.build:
	kind build node-image --base-image ${KIND_BASE_IMG}
	
cluster.up:
	kind create cluster --image kindest/node:latest --name $(CLUSTER) --config manifests/kind-conf.yaml
	kind load docker-image $(SCHED_IMAGE) --name $(CLUSTER)
	kind load docker-image $(POD_IMAGE) --name $(CLUSTER)
	kubectl get clusterrole system:kube-scheduler -o yaml | yq e '.rules[] |= (with(select(.resources[] | select(. == "pods")); .verbs += "update"))' > manifests/clusterrole-sched.yaml
	kubectl apply -f manifests/clusterrole-sched.yaml
	rm manifests/clusterrole-sched.yaml

cluster.down:
	kind delete cluster --name $(CLUSTER)

podlistener.up:
	go build -o app . && ./app

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

generate: clean
	sh gen.sh $(FILE)

exp:
	sh exp.sh

deploy: deploy.prios deploy.jobs

deploy.prios:
	kubectl apply -f prios

deploy.jobs:
	kubectl apply -f jobs

delete.jobs:
	kubectl delete jobs -l jobgroup=countdown
	kubectl delete pods -l jobgroup=countdown
	kubectl delete pods -l jobgroup=stress
print.pods:
	kubectl get pods -o custom-columns=$(POD_COLUMNS)

plot:
	@mkdir -p $(TEMP_FOLDER) && \
	kubectl get pods -o custom-columns=$(POD_COLUMNS) > $(TEMP_FOLDER)/pod_status.log && \
	python graph.py $(TEMP_FOLDER)/pod_status.log

log:
	@mkdir -p out
	@kubectl get pods -o custom-columns=$(POD_COLUMNS) > out/pod_status_$(CURRENT_UNIX).log
	@kubectl describe pods > out/pod_desc_$(CURRENT_UNIX).log

clean:
	rm -rf jobs $(TEMP_FOLDER)
