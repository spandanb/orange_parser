#!/bin/bash

#EXECUTION PATH, i.e. location of parser
EXECPATH=/home/ubuntu/orange/parser 
#The CURRENT DIR
CURPATH=$EXECPATH/evaluation  
#The results file
RESULTS=$CURPATH/results

cd $EXECPATH 
cat /dev/null > $RESULTS

for i in `seq 1 100`;
do 
    ./parser.py -f topology_simple.yaml >> $RESULTS
done

cd $CURPATH
result=python get_avg.py 
echo "AVG=$result" >>  $RESULTS
