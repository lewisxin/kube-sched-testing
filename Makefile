FILE := countdown-tmpl.yaml
POD_COLUMNS := "NAME:.metadata.name,POD_CREATED:.metadata.creationTimestamp,POD_STARTED:.status.startTime,STARTED:.status.containerStatuses[*].state.*.startedAt,FINISHED:.status.containerStatuses[*].state.*.finishedAt,NODE:.spec.nodeName,STATUS:.status.containerStatuses[*].state.*.reason,DDL:.metadata.annotations.*,PRIORITY:.spec.priority"
CURRENT_UNIX=$$(date +%s)

all: generate

generate: clean
	sh gen.sh $(FILE)

deploy: deploy.prios deploy.jobs

deploy.prios:
	kubectl apply -f prios

deploy.jobs:
	kubectl apply -f jobs

print.pods:
	kubectl get pods -o custom-columns=$(POD_COLUMNS)

log:
	@mkdir -p out
	@kubectl get pods -o custom-columns=$(POD_COLUMNS) > out/pod_status_$(CURRENT_UNIX).log
	@kubectl describe pods > out/pod_desc_$(CURRENT_UNIX).log

clean:
	rm -rf jobs
