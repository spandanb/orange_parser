#!/bin/bash

#EXECUTION PATH, i.e. location of parser
EXECPATH=/home/ubuntu/orange/parser 
#The CURRENT DIR
CURPATH=$EXECPATH/evaluation  
#The results file
RESULTS=$CURPATH/results
MRESULTS=$CURPATH/mresults #meta-results

cd $EXECPATH 
cat /dev/null > $RESULTS
cat /dev/null > $MRESULTS

for j in `seq 1 5`;
do
    for i in `seq 1 10`;
    do 
        ./parser.py -f "topo/topology$j.yaml" >> $RESULTS$j
    done
done

cd $CURPATH
for j in `seq 1 5`;
do
    result=`python get_avg.py $RESULTS$j`
    echo "AVG$j=$result" >>  $MRESULTS
done
