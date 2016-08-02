#!/bin/bash

#EXECUTION PATH, i.e. location of parser
EXECPATH=/home/ubuntu/orange/parser 
#The CURRENT DIR
CURPATH=$EXECPATH/evaluation  
#The results file
RESULTS=$CURPATH/results
MRESULTS=$CURPATH/mresults #meta-results

for j in `seq 1 5`; 
do
    cat /dev/null > $RESULTS$j
done
cat /dev/null > $MRESULTS

cd $EXECPATH 
for j in `seq 1 5`;
do
    for i in `seq 1 5`;
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
