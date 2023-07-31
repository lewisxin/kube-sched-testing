# Expand the template into multiple files, one for each item to be processed.
mkdir ./jobs
t=0
for i in {10..40}
do
  if [ $t -eq 1 ]; then
      prio="high-priority"
      t=0
  else
      prio="low-priority"
      t=1
  fi
  ddl=$(((i % 3 + 1) * 10))
  cat countdown-templ.yaml | sed "s/\$ID/$i/" | sed "s/\$DDL/$ddl/" | sed "s/\$PRIO/$prio/" > ./jobs/job-$i.yaml
done
