make deploy.prios
for i in {1..3}
do
    echo "running experiment $i"
    make delete.jobs
    make deploy.jobs
    res=$(make print.pods | grep "none")
    while [ -n "$res" ]
    do
        echo "waiting for jobs to finish..."
        sleep 10
        res=$(make print.pods | grep "none")
    done
    make plot
    sleep 3
done
