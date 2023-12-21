# Experiment on remote server

## Run without CPU limits -> Jobs competing for resources
### run individually

```bash
root@altra80:/home/xin/go/src/github.com/kube-sched-testing# k get jobs
NAME                          COMPLETIONS   DURATION   AGE
car-evaluation-params-sweep   8/8           5m9s       10m
spotify-songs-params-sweep    9/9           4m13s      16m
video-transcoding-game1       3/3           21s        23m
video-transcoding-game2       3/3           32s        18m
video-transcoding-game3       3/3           36s        101s
video-transcoding-trailer1    3/3           63s        23m
video-transcoding-trailer2    3/3           43s        17m
video-transcoding-trailer3    3/3           64s        3m20s
video-transcoding-video1      3/3           119s       20m
video-transcoding-video2      3/3           20s        4m52s
video-transcoding-video3      3/3           15s        22s
video-transcoding-video4      3/3           11s        16s
```

### run everything together

```bash
root@altra80:/home/xin/go/src/github.com/kube-sched-testing# k get jobs
NAME                          COMPLETIONS   DURATION   AGE
car-evaluation-params-sweep   8/8           6m23s      6m43s
spotify-songs-params-sweep    9/9           4m32s      6m43s
video-transcoding-game1       3/3           27s        6m59s
video-transcoding-game2       3/3           2m7s       6m49s
video-transcoding-game3       3/3           2m46s      6m41s
video-transcoding-trailer1    3/3           3m18s      6m59s
video-transcoding-trailer2    3/3           3m9s       6m47s
video-transcoding-trailer3    3/3           3m28s      6m43s
video-transcoding-video1      3/3           4m38s      6m54s
video-transcoding-video2      3/3           105s       6m44s
video-transcoding-video3      3/3           87s        6m39s
video-transcoding-video4      3/3           64s        6m36s
```

### without param sweep

```bash
root@altra80:/home/xin/go/src/github.com/kube-sched-testing# k get jobs
NAME                         COMPLETIONS   DURATION   AGE
video-transcoding-game1      3/3           22s        2m53s
video-transcoding-game2      3/3           58s        2m43s
video-transcoding-game3      3/3           66s        2m36s
video-transcoding-trailer1   3/3           94s        2m53s
video-transcoding-trailer2   3/3           78s        2m41s
video-transcoding-trailer3   3/3           91s        2m37s
video-transcoding-video1     3/3           2m36s      2m48s
video-transcoding-video2     3/3           47s        2m38s
video-transcoding-video3     3/3           40s        2m33s
video-transcoding-video4     3/3           31s        2m30s
```

### with even less transcoding jobs

```bash
root@altra80:/home/xin/go/src/github.com/kube-sched-testing# k get jobs
NAME                         COMPLETIONS   DURATION   AGE
video-transcoding-game1      3/3           21s        3m18s
video-transcoding-game2      3/3           41s        3m8s
video-transcoding-trailer1   3/3           81s        3m18s
video-transcoding-trailer2   3/3           62s        3m6s
video-transcoding-video1     3/3           2m20s      3m13s
video-transcoding-video2     3/3           32s        3m3s
```

## with limit (4) CPUs

### run only 6 transcode jobs

```bash
root@altra80:/home/xin/go/src/github.com/kube-sched-testing# k get jobs
NAME                         COMPLETIONS   DURATION   AGE
video-transcoding-game1      3/3           46s        9m17s
video-transcoding-game2      3/3           88s        9m7s
video-transcoding-trailer1   3/3           4m5s       9m17s
video-transcoding-trailer2   3/3           2m11s      9m5s
video-transcoding-video1     3/3           8m57s      9m12s
video-transcoding-video2     3/3           60s        9m2s
```

### run only 1 transcode job

```bash
root@altra80:/home/xin/go/src/github.com/kube-sched-testing# k get jobs
NAME                      COMPLETIONS   DURATION   AGE
video-transcoding-game1   3/3           76s        80s
```

## with limit (8) CPUs for transcode jobs

### run only 6 transcode jobs -> almost 1/2 time compared to 4 CPUs (expected)

```bash
root@altra80:/home/xin/go/src/github.com/kube-sched-testing# k get jobs
NAME                         COMPLETIONS   DURATION   AGE
video-transcoding-game1      3/3           26s        4m37s
video-transcoding-game2      3/3           44s        4m27s
video-transcoding-trailer1   3/3           110s       4m37s
video-transcoding-trailer2   3/3           75s        4m25s
video-transcoding-video1     3/3           4m22s      4m32s
video-transcoding-video2     3/3           34s        4m22s
```

### run all jobs -> still competing CPU -> every node thinks it has the entire 80 CPU allocatable -> need to figure out a way to limit this

> https://github.com/kubernetes-sigs/kind/issues/1578#issuecomment-636564538

```bash
root@altra80:/home/xin/go/src/github.com/kube-sched-testing# k get jobs
NAME                          COMPLETIONS   DURATION   AGE
car-evaluation-params-sweep   8/8           6m41s      10m
spotify-songs-params-sweep    9/9           4m51s      10m
video-transcoding-game1       3/3           37s        11m
video-transcoding-game2       3/3           106s       10m
video-transcoding-game3       3/3           119s       10m
video-transcoding-trailer1    3/3           3m14s      11m
video-transcoding-trailer2    3/3           2m20s      10m
video-transcoding-trailer3    3/3           3m13s      10m
video-transcoding-video1      3/3           4m36s      10m
video-transcoding-video2      3/3           82s        10m
video-transcoding-video3      3/3           68s        10m
video-transcoding-video4      3/3           50s        10m
```

## Configure each node with only 15 available CPUs
### Run all jobs with equal priority, some were waiting for available resources
```bash
NAME                          COMPLETIONS   DURATION   AGE
car-evaluation-params-sweep   8/8           8m28s      9m17s
spotify-songs-params-sweep    9/9           7m57s      9m17s
video-transcoding-game1       3/3           27s        9m32s
video-transcoding-game2       3/3           7m23s      9m22s
video-transcoding-game3       3/3           6m24s      9m15s
video-transcoding-trailer1    3/3           93s        9m32s
video-transcoding-trailer2    3/3           8m26s      9m20s
video-transcoding-trailer3    3/3           6m27s      9m16s
video-transcoding-video1      3/3           3m42s      9m27s
video-transcoding-video2      3/3           2m46s      9m17s
video-transcoding-video3      3/3           6m47s      9m12s
video-transcoding-video4      3/3           6m49s      9m9s
```


### Run individual jobs one by one to benchmark the execution time
```bash
NAME                          COMPLETIONS   DURATION   AGE
car-evaluation-params-sweep   8/8           5m15s      5m18s
spotify-songs-params-sweep    9/9           4m3s       10m
video-transcoding-game1       3/3           29s        19m
video-transcoding-game2       3/3           67s        22m
video-transcoding-game3       3/3           72s        14m
video-transcoding-trailer1    3/3           2m1s       18m
video-transcoding-trailer2    3/3           90s        20m
video-transcoding-trailer3    3/3           2m12s      16m
video-transcoding-video1      3/3           4m34s      18m
video-transcoding-video2      3/3           40s        16m
video-transcoding-video3      3/3           31s        13m
video-transcoding-video4      3/3           25s        12m
```

## Default Scheduler
```bash
NAME                          COMPLETIONS   DURATION   AGE
car-evaluation-params-sweep   8/8           5m20s      19m
spotify-songs-params-sweep    9/9           9m8s       19m
video-transcoding-game1       3/3           27s        19m
video-transcoding-game2       3/3           7m36s      19m
video-transcoding-game3       3/3           6m21s      19m
video-transcoding-trailer1    3/3           93s        19m
video-transcoding-trailer2    3/3           8m14s      19m
video-transcoding-trailer3    3/3           7m9s       19m
video-transcoding-video1      3/3           3m42s      19m
video-transcoding-video2      3/3           7m49s      19m
video-transcoding-video3      3/3           6m39s      19m
video-transcoding-video4      3/3           6m50s      19m
```

## LLF
```bash
NAME                          COMPLETIONS   DURATION   AGE
car-evaluation-params-sweep   8/8           11m        12m
spotify-songs-params-sweep    9/9           8m54s      12m
video-transcoding-game1       3/3           98s        12m
video-transcoding-game2       3/3           87s        12m
video-transcoding-game3       3/3           6m21s      11m
video-transcoding-trailer1    3/3           4m50s      12m
video-transcoding-trailer2    3/3           2m4s       12m
video-transcoding-trailer3    3/3           4m12s      11m
video-transcoding-video1      3/3           7m45s      12m
video-transcoding-video2      3/3           77s        12m
video-transcoding-video3      3/3           9m33s      11m
video-transcoding-video4      3/3           2m18s      11m
```


EDF
```bash
NAME                          COMPLETIONS   DURATION   AGE
car-evaluation-params-sweep   8/8           14m        14m
spotify-songs-params-sweep    9/9           8m36s      14m
video-transcoding-game1       3/3           35s        14m
video-transcoding-game2       3/3           5m15s      14m
video-transcoding-game3       3/3           113s       14m
video-transcoding-trailer1    3/3           6m52s      14m
video-transcoding-trailer2    3/3           3m23s      14m
video-transcoding-trailer3    3/3           4m57s      14m
video-transcoding-video1      3/3           7m45s      14m
video-transcoding-video2      3/3           53s        14m
video-transcoding-video3      3/3           2m5s       14m
video-transcoding-video4      3/3           44s        14m
```