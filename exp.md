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
car-evaluation-params-sweep   8/8           4m44s      6m30s
spotify-songs-params-sweep    7/7           5m21s      6m30s
video-transcoding-game1       3/3           3m20s      6m25s
video-transcoding-game2       3/3           4m49s      6m20s
video-transcoding-game3       2/3           6m13s      6m13s
video-transcoding-trailer1    3/3           3m18s      6m25s
video-transcoding-trailer2    3/3           4m45s      6m18s
video-transcoding-trailer3    3/3           6m13s      6m14s
video-transcoding-video1      3/3           5m37s      6m25s
video-transcoding-video2      3/3           4m22s      6m15s
video-transcoding-video3      3/3           4m36s      6m10s
video-transcoding-video4      3/3           4m33s      6m7s
```
### Metrics
```log
                           Name  Job_Start     Job_End  Deadline   Resp_Time    Lateness   Tardiness  DDL_Missed
ID                                                                                                              
1    spotify-songs-params-sweep        0.0  320.633437     360.0  320.633437  -39.366563    0.000000           0
2   car-evaluation-params-sweep        0.0  284.551168     360.0  284.551168  -75.448832    0.000000           0
3       video-transcoding-game1        5.0  205.384797     245.0  200.384797  -39.615203    0.000000           0
4    video-transcoding-trailer1        5.0  202.436967     245.0  197.436967  -42.563033    0.000000           0
5      video-transcoding-video1        5.0  341.803490     245.0  336.803490   96.803490   96.803490           1
6       video-transcoding-game2       10.0  299.232564     250.0  289.232564   49.232564   49.232564           1
7    video-transcoding-trailer2       12.0  296.681850     132.0  284.681850  164.681850  164.681850           1
8      video-transcoding-video2       15.0  276.687010     135.0  261.687010  141.687010  141.687010           1
9    video-transcoding-trailer3       16.0  388.825307     256.0  372.825307  132.825307  132.825307           1
10      video-transcoding-game3       17.0  329.709600     317.0  312.709600   12.709600   12.709600           1
11     video-transcoding-video3       20.0  295.682976     140.0  275.682976  155.682976  155.682976           1
12     video-transcoding-video4       23.0  296.660936     143.0  273.660936  153.660936  153.660936           1
Total Deadline Misses: 8
Max Resp Time: 372.825s
Max Lateness: 164.682s
Max Tardiness: 164.682s
Avg Resp Time: 284.191s
Avg Tardiness: 75.607s
Avg Lateness: 59.191s
```

## Default with kill-based Preemption
```bash
NAME                          COMPLETIONS   DURATION   AGE
car-evaluation-params-sweep   8/8           6m41s      31m
spotify-songs-params-sweep    7/7           7m51s      31m
video-transcoding-game1       3/3           111s       31m
video-transcoding-game2       3/3           2m41s      31m
video-transcoding-game3       3/3           3m4s       31m
video-transcoding-trailer1    3/3           3m23s      31m
video-transcoding-trailer2    3/3           2m14s      31m
video-transcoding-trailer3    3/3           3m14s      31m
video-transcoding-video1      3/3           4m35s      31m
video-transcoding-video2      3/3           79s        31m
video-transcoding-video3      3/3           63s        31m
video-transcoding-video4      3/3           52s        31m
```

### Metrics
```log
                           Name  Job_Start     Job_End  Deadline   Resp_Time    Lateness   Tardiness  DDL_Missed
ID                                                                                                              
1    spotify-songs-params-sweep        0.0  471.036485     360.0  471.036485  111.036485  111.036485           1
2   car-evaluation-params-sweep        0.0  400.852163     360.0  400.852163   40.852163   40.852163           1
3       video-transcoding-game1        5.0  115.429392     245.0  110.429392 -129.570608    0.000000           0
4    video-transcoding-trailer1        5.0  207.473034     245.0  202.473034  -37.526966    0.000000           0
5      video-transcoding-video1        5.0  279.665920     245.0  274.665920   34.665920   34.665920           1
6       video-transcoding-game2       10.0  171.368093     250.0  161.368093  -78.631907    0.000000           0
7    video-transcoding-trailer2       12.0  145.564370     132.0  133.564370   13.564370   13.564370           1
8      video-transcoding-video2       15.0   94.158458     135.0   79.158458  -40.841542    0.000000           0
9    video-transcoding-trailer3       16.0  209.312467     256.0  193.312467  -46.687533    0.000000           0
10      video-transcoding-game3       17.0  200.396902     317.0  183.396902 -116.603098    0.000000           0
11     video-transcoding-video3       20.0   83.165725     140.0   63.165725  -56.834275    0.000000           0
12     video-transcoding-video4       23.0   75.070962     143.0   52.070962  -67.929038    0.000000           0
Total Deadline Misses: 4
Max Resp Time: 471.036s
Max Lateness: 111.036s
Max Tardiness: 111.036s
Avg Resp Time: 193.791s
Avg Tardiness: 16.677s
Avg Lateness: -31.209s
```


## LLF
```bash
NAME                          COMPLETIONS   DURATION   AGE
car-evaluation-params-sweep   8/8           6m59s      7m43s
spotify-songs-params-sweep    7/7           6m15s      7m43s
video-transcoding-game1       3/3           113s       7m38s
video-transcoding-game2       3/3           2m7s       7m33s
video-transcoding-game3       3/3           3m53s      7m26s
video-transcoding-trailer1    3/3           2m38s      7m38s
video-transcoding-trailer2    3/3           97s        7m31s
video-transcoding-trailer3    3/3           3m29s      7m27s
video-transcoding-video1      3/3           3m53s      7m38s
video-transcoding-video2      3/3           63s        7m28s
video-transcoding-video3      3/3           58s        7m23s
video-transcoding-video4      3/3           82s        7m20s
```
### Metrics
```log
                           Name  Job_Start     Job_End  Deadline   Resp_Time    Lateness  Tardiness  DDL_Missed
ID                                                                                                             
1    spotify-songs-params-sweep        0.0  374.602021     360.0  374.602021   14.602021  14.602021           1
2   car-evaluation-params-sweep        0.0  418.789765     360.0  418.789765   58.789765  58.789765           1
3       video-transcoding-game1        5.0  117.998959     245.0  112.998959 -127.001041   0.000000           0
4    video-transcoding-trailer1        5.0  163.108250     245.0  158.108250  -81.891750   0.000000           0
5      video-transcoding-video1        5.0  237.292861     245.0  232.292861   -7.707139   0.000000           0
6       video-transcoding-game2       10.0  136.406343     250.0  126.406343 -113.593657   0.000000           0
7    video-transcoding-trailer2       12.0  109.036952     132.0   97.036952  -22.963048   0.000000           0
8      video-transcoding-video2       15.0   78.095011     135.0   63.095011  -56.904989   0.000000           0
9    video-transcoding-trailer3       16.0  225.271731     256.0  209.271731  -30.728269   0.000000           0
10      video-transcoding-game3       17.0  249.358082     317.0  232.358082  -67.641918   0.000000           0
11     video-transcoding-video3       20.0   77.849630     140.0   57.849630  -62.150370   0.000000           0
12     video-transcoding-video4       23.0  104.851574     143.0   81.851574  -38.148426   0.000000           0
Total Deadline Misses: 2
Max Resp Time: 418.79s
Max Lateness: 58.79s
Max Tardiness: 58.79s
Avg Resp Time: 180.388s
Avg Tardiness: 6.116s
Avg Lateness: -44.612s
```


## EDF
```bash
NAME                          COMPLETIONS   DURATION   AGE
car-evaluation-params-sweep   8/8           5m47s      7m7s
spotify-songs-params-sweep    7/7           7m4s       7m7s
video-transcoding-game1       3/3           66s        7m2s
video-transcoding-game2       3/3           109s       6m58s
video-transcoding-game3       3/3           2m24s      6m51s
video-transcoding-trailer1    3/3           2m36s      7m2s
video-transcoding-trailer2    3/3           112s       6m56s
video-transcoding-trailer3    3/3           2m56s      6m52s
video-transcoding-video1      3/3           4m24s      7m2s
video-transcoding-video2      3/3           51s        6m52s
video-transcoding-video3      3/3           39s        6m47s
video-transcoding-video4      3/3           32s        6m44s
```

```log
                           Name  Job_Start     Job_End  Deadline   Resp_Time    Lateness  Tardiness  DDL_Missed
ID                                                                                                             
1    spotify-songs-params-sweep        0.0  423.854227     360.0  423.854227   63.854227  63.854227           1
2   car-evaluation-params-sweep        0.0  347.171356     360.0  347.171356  -12.828644   0.000000           0
3       video-transcoding-game1        5.0   70.589248     245.0   65.589248 -174.410752   0.000000           0
4    video-transcoding-trailer1        5.0  160.732073     245.0  155.732073  -84.267927   0.000000           0
5      video-transcoding-video1        5.0  268.987780     245.0  263.987780   23.987780  23.987780           1
6       video-transcoding-game2       10.0  118.815626     250.0  108.815626 -131.184374   0.000000           0
7    video-transcoding-trailer2       12.0  124.273966     132.0  112.273966   -7.726034   0.000000           0
8      video-transcoding-video2       15.0   65.913704     135.0   50.913704  -69.086296   0.000000           0
9    video-transcoding-trailer3       16.0  191.493586     256.0  175.493586  -64.506414   0.000000           0
10      video-transcoding-game3       17.0  161.148970     317.0  144.148970 -155.851030   0.000000           0
11     video-transcoding-video3       20.0   58.538946     140.0   38.538946  -81.461054   0.000000           0
12     video-transcoding-video4       23.0   54.531816     143.0   31.531816  -88.468184   0.000000           0
Total Deadline Misses: 2
Max Resp Time: 423.854s
Max Lateness: 63.854s
Max Tardiness: 63.854s
Avg Resp Time: 159.838s
Avg Tardiness: 7.32s
Avg Lateness: -65.162s
```