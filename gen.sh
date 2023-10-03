#!/bin/bash
# Expand the template into multiple files, one for each item to be processed.
mkdir ./jobs
FILENAME="templates/${1:-countdown-ddl-tmpl.yaml}"
EXECUTION_TIMES=(10 20 8 5 15 25 30 5 9 10)
DEADLINES=("10s" "25s" "10s" "10s" "20s" "30s" "32s" "8s" "10s" "10s")
PRIORITIES=("high-priority", "low-priority")

for i in ${!EXECUTION_TIMES[@]}; do
  jid=$(printf "%02d" $((i+1)))
  t=${EXECUTION_TIMES[$i]}
  ddl=${DEADLINES[$i]}
  prio=${PRIORITIES[$((i%2))]}
  cat $FILENAME | sed "s/\$ID/$jid/" | sed "s/\$DDL/$ddl/" | sed "s/\$EXEC_TIME/$t/" | sed "s/\$PRIO/$prio/" > ./jobs/job-$jid.yaml
done
