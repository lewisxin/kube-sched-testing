#!/bin/bash
# Expand the template into multiple files, one for each item to be processed.
mkdir ./jobs
filename="templates/${1:-countdown-ddl-tmpl.yaml}"
flag=0
for i in 1 2 3 4 5 6 7 8 9 10
do
  if [ $flag -eq 1 ]; then
      prio="high-priority"
      flag=0
  else
      prio="low-priority"
      flag=1
  fi
  ddl=$(((i % 3 + 1) * 10))
  jid=$(printf "%02d" $i)
  cat $filename | sed "s/\$ID/$jid/" | sed "s/\$DDL/$ddl/" | sed "s/\$PRIO/$prio/" > ./jobs/job-$jid.yaml
done
