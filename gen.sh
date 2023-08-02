# Expand the template into multiple files, one for each item to be processed.
mkdir ./jobs
filename="${1:-countdown-tmpl.yaml}"
flag=0
for i in {01..30}
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
