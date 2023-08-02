FILE:=countdown-tmpl.yaml
CLUSTER:=k8s-multi-node
TEMP_FOLDER=temp
POD_COLUMNS:="NAME:.metadata.name,POD_CREATED:.metadata.creationTimestamp,POD_STARTED:.status.startTime,POD_SCHED:.status.conditions[?(@.type==\"PodScheduled\")].lastTransitionTime,STARTED:.status.containerStatuses[*].state.*.startedAt,FINISHED:.status.containerStatuses[*].state.*.finishedAt,NODE:.spec.nodeName,STATUS:.status.containerStatuses[*].state.*.reason,DDL:.metadata.annotations.*,PRIORITY:.spec.priority"
CURRENT_UNIX=$$(date +%s)

all: generate

cluster.up:
	kind create cluster --name $(CLUSTER) --config kind-conf.yaml
	kind load docker-image localhost:5000/scheduler-plugins/kube-scheduler:latest --name $(CLUSTER)

cluster.down:
	kind delete cluster --name $(CLUSTER)

config.simpleddlscheduler:
	docker cp simpleddl.yaml $(CLUSTER)-control-plane:/etc/kubernetes/.
	docker cp kube-scheduler-simpleddl.yaml $(CLUSTER)-control-plane:/etc/kubernetes/.
	docker exec $(CLUSTER)-control-plane cp /etc/kubernetes/manifests/kube-scheduler.yaml /etc/kubernetes/kube-scheduler.yaml
	docker exec $(CLUSTER)-control-plane cp /etc/kubernetes/kube-scheduler-simpleddl.yaml /etc/kubernetes/manifests/kube-scheduler.yaml

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
