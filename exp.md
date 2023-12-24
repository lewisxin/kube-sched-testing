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



## Job Details
```csv
id,arrival_time,execution_time,ddl,cpu_limit,template,meta1,meta2,meta3
01,0,5m36s,6m,4,hyperparam,spotify-songs,7,spotify_songs
02,0,3m50s,6m,7,hyperparam,car-evaluation,8,car_evaluation
03,5,2m26s,4m,3,transcoding,game1,webm,
04,5,2m48s,4m,7,transcoding,trailer1,mp4,
05,5,3m31s,4m,10,transcoding,video1,mp4,
06,10,3m,4m,3,transcoding,game2,webm,
07,12,1m37s,2m,7,transcoding,trailer2,mp4,
08,15,1m16s,2m,5,transcoding,video2,mp4,
09,16,2m27s,4m,7,transcoding,trailer3,mp4,
10,17,3m31s,5m,3,transcoding,game3,webm,
11,20,48s,2m,5,transcoding,video3,mp4,
12,23,32s,2m,5,transcoding,video4,mp4,
```
### Benchmark Individual Jobs
```bash
NAME                          COMPLETIONS   DURATION   AGE
car-evaluation-params-sweep   8/8           3m48s      29m
spotify-songs-params-sweep    7/7           5m36s      5m44s
video-transcoding-game1       3/3           2m26s      48m
video-transcoding-game2       3/3           3m         44m
video-transcoding-game3       3/3           3m31s      5m52s
video-transcoding-trailer1    3/3           2m48s      50m
video-transcoding-trailer2    3/3           97s        39m
video-transcoding-trailer3    3/3           2m27s      5m54s
video-transcoding-video1      3/3           3m31s      40m
video-transcoding-video2      3/3           76s        23m
video-transcoding-video3      3/3           48s        72s
video-transcoding-video4      3/3           32s        70s
```

## Default Scheduler
```bash
NAME                          COMPLETIONS   DURATION   AGE
car-evaluation-params-sweep   8/8           4m39s      10m
spotify-songs-params-sweep    7/7           5m27s      10m
video-transcoding-game1       3/3           61s        10m
video-transcoding-game2       3/3           4m42s      10m
video-transcoding-game3       3/3           7m19s      10m
video-transcoding-trailer1    3/3           4m24s      10m
video-transcoding-trailer2    3/3           4m44s      10m
video-transcoding-trailer3    3/3           6m4s       10m
video-transcoding-video1      3/3           5m2s       10m
video-transcoding-video2      3/3           4m26s      10m
video-transcoding-video3      3/3           4m53s      10m
video-transcoding-video4      3/3           4m47s      10m
```
### Metrics
```log
                           Name  Job_Start     Job_End  Deadline   Resp_Time    Lateness   Tardiness  DDL_Missed
ID                                                                                                              
1    spotify-songs-params-sweep        0.0  327.189983     360.0  327.189983  -32.810017    0.000000           0
2   car-evaluation-params-sweep        0.0  279.065020     360.0  279.065020  -80.934980    0.000000           0
3       video-transcoding-game1        5.0   66.268689     245.0   61.268689 -178.731311    0.000000           0
4    video-transcoding-trailer1        5.0  268.990877     245.0  263.990877   23.990877   23.990877           1
5      video-transcoding-video1        5.0  306.689358     245.0  301.689358   61.689358   61.689358           1
6       video-transcoding-game2       10.0  292.066154     250.0  282.066154   42.066154   42.066154           1
7    video-transcoding-trailer2       12.0  295.523108     132.0  283.523108  163.523108  163.523108           1
8      video-transcoding-video2       15.0  280.992872     135.0  265.992872  145.992872  145.992872           1
9    video-transcoding-trailer3       16.0  380.180673     256.0  364.180673  124.180673  124.180673           1
10      video-transcoding-game3       17.0  455.900189     317.0  438.900189  138.900189  138.900189           1
11     video-transcoding-video3       20.0  313.121406     140.0  293.121406  173.121406  173.121406           1
12     video-transcoding-video4       23.0  310.089360     143.0  287.089360  167.089360  167.089360           1
Total Deadline Misses: 9
Max Resp Time: 438.9s
Max Lateness: 173.121s
Max Tardiness: 173.121s
Avg Resp Time: 287.34s
Avg Tardiness: 86.713s
Avg Lateness: 62.34s
```

## LLF
```bash
NAME                          COMPLETIONS   DURATION   AGE
car-evaluation-params-sweep   8/8           6m36s      19m
spotify-songs-params-sweep    7/7           7m18s      19m
video-transcoding-game1       3/3           68s        19m
video-transcoding-game2       3/3           2m13s      19m
video-transcoding-game3       3/3           2m9s       19m
video-transcoding-trailer1    3/3           2m31s      19m
video-transcoding-trailer2    3/3           106s       19m
video-transcoding-trailer3    3/3           2m18s      19m
video-transcoding-video1      3/3           3m51s      19m
video-transcoding-video2      3/3           56s        19m
video-transcoding-video3      3/3           56s        19m
video-transcoding-video4      3/3           38s        19m
```
### Metrics
```log
                           Name  Job_Start     Job_End  Deadline   Resp_Time    Lateness  Tardiness  DDL_Missed
ID                                                                                                             
1    spotify-songs-params-sweep        0.0  437.549339     360.0  437.549339   77.549339  77.549339           1
2   car-evaluation-params-sweep        0.0  395.411142     360.0  395.411142   35.411142  35.411142           1
3       video-transcoding-game1        5.0   72.351119     245.0   67.351119 -172.648881   0.000000           0
4    video-transcoding-trailer1        4.0  154.776072     244.0  150.776072  -89.223928   0.000000           0
5      video-transcoding-video1        4.0  235.211825     244.0  231.211825   -8.788175   0.000000           0
6       video-transcoding-game2        9.0  141.877716     249.0  132.877716 -107.122284   0.000000           0
7    video-transcoding-trailer2       11.0  116.692939     131.0  105.692939  -14.307061   0.000000           0
8      video-transcoding-video2       14.0   69.697795     134.0   55.697795  -64.302205   0.000000           0
9    video-transcoding-trailer3       15.0  152.817702     255.0  137.817702 -102.182298   0.000000           0
10      video-transcoding-game3       16.0  144.950674     316.0  128.950674 -171.049326   0.000000           0
11     video-transcoding-video3       19.0   74.577079     139.0   55.577079  -64.422921   0.000000           0
12     video-transcoding-video4       22.0   59.671712     142.0   37.671712  -82.328288   0.000000           0
Total Deadline Misses: 2
Max Resp Time: 437.549s
Max Lateness: 77.549s
Max Tardiness: 77.549s
Avg Resp Time: 161.382s
Avg Tardiness: 9.413s
Avg Lateness: -63.618s
```


## EDF
```bash
NAME                          COMPLETIONS   DURATION   AGE
car-evaluation-params-sweep   8/8           6m45s      8m13s
spotify-songs-params-sweep    7/7           7m4s       8m13s
video-transcoding-game1       3/3           57s        8m8s
video-transcoding-game2       3/3           107s       8m3s
video-transcoding-game3       3/3           2m24s      7m56s
video-transcoding-trailer1    3/3           2m31s      8m8s
video-transcoding-trailer2    3/3           110s       8m1s
video-transcoding-trailer3    3/3           2m44s      7m57s
video-transcoding-video1      3/3           4m28s      8m8s
video-transcoding-video2      3/3           59s        7m58s
video-transcoding-video3      3/3           42s        7m53s
video-transcoding-video4      3/3           27s        7m50s
```

```log
                           Name  Job_Start     Job_End  Deadline   Resp_Time    Lateness  Tardiness  DDL_Missed
ID                                                                                                             
1    spotify-songs-params-sweep        0.0  423.840909     360.0  423.840909   63.840909  63.840909           1
2   car-evaluation-params-sweep        0.0  404.634126     360.0  404.634126   44.634126  44.634126           1
3       video-transcoding-game1        5.0   61.947829     245.0   56.947829 -183.052171   0.000000           0
4    video-transcoding-trailer1        5.0  156.148177     245.0  151.148177  -88.851823   0.000000           0
5      video-transcoding-video1        5.0  272.391347     245.0  267.391347   27.391347  27.391347           1
6       video-transcoding-game2       10.0  117.138916     250.0  107.138916 -132.861084   0.000000           0
7    video-transcoding-trailer2       12.0  122.240725     132.0  110.240725   -9.759275   0.000000           0
8      video-transcoding-video2       15.0   73.750500     135.0   58.750500  -61.249500   0.000000           0
9    video-transcoding-trailer3       16.0  180.299263     256.0  164.299263  -75.700737   0.000000           0
10      video-transcoding-game3       17.0  160.470550     317.0  143.470550 -156.529450   0.000000           0
11     video-transcoding-video3       20.0   61.687595     140.0   41.687595  -78.312405   0.000000           0
12     video-transcoding-video4       23.0   49.985081     143.0   26.985081  -93.014919   0.000000           0
Total Deadline Misses: 3
Max Resp Time: 423.841s
Max Lateness: 63.841s
Max Tardiness: 63.841s
Avg Resp Time: 163.045s
Avg Tardiness: 11.322s
Avg Lateness: -61.955s
```