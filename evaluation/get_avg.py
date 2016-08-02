
import sys

with open(sys.argv[1]) as fptr:
    agg = 0.0
    count = 0
    for line in fptr: 
        try:
            agg += float(line)    
            count += 1
        except ValueError:
            pass
    print agg/count


