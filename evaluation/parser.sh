#!/bin/bash

#EXECUTION PATH, i.e. location of parser
EXECPATH=/home/ubuntu/orange/parser 
#The CURRENT DIR
CURPATH=$EXECPATH/evaluation  
#Prototype for results file
RESULTS=$CURPATH/results
MRESULTS=$CURPATH/mresults #meta-results

cd $EXECPATH 
cat /dev/null > $MRESULTS

for j in `seq 4 5`; do
    echo "Running topology $j"

    for p in savi aws; do
        #Nuke the results file
        cat /dev/null > $RESULTS$j.$p

        for i in `seq 1 1`; do
            echo "Provider=$p  Iteration=$i"
            ./parser.py -f "topo/topology$j.$p.yaml" >> $RESULTS$j.$p
            ./parser.py -c 
        done
    done
done

cd $CURPATH
for j in `seq 4 5`; do
    for p in "savi" "aws"; do 
        result=`python get_avg.py $RESULTS$j.$p`
        echo "AVG$j $p=$result" >>  $MRESULTS
    done
done
