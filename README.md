# trstats
Computer Networks 

```
python3 trstats.py -o output [-n NUM_RUNS] [-t TARGET] [-d RUN_DELAY] [-m MAX_HOPS] [--test TEST_DIR]
```

This project uses Python to create a command line tool that automatically executes traceroute multiple times towards a target domain name or IP address specified as command line parameter. Based on multiple traceroute executions, the program will need to derive latency statistics for each hop between the traceroute client and the target machine.

To allow for repeatable tests, the program also allows reading pre-generated traceroute output traces stored on multiple text files (one text output trace per file). Based on this pre-generated output, the program will need to compute the latency statistics as for the case of live traceroute execution. 




