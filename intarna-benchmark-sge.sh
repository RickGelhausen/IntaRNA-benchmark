#!/bin/bash
#$ -N uv
#$ -cwd 
#$ -pe smp 20 TODO TODO TODO
#$ -l h_vmem=2G
#$ -o /media/azhra/hdd/git/Cluster/intaRNA-benchmark/
#$ -e /media/azhra/hdd/git/Cluster/intaRNA-benchmark/
#$ -j y
#$ -M gelhausr@informatik.uni-freiburg.de
#$ -m a

source activate intarna-benchmark

# /scratch/bi03/rick/
# Variables
intaRNAbinary="../intaRNA/src/bin/"
inputPath="./input/"
outputPath="../intaRNA-output/"
intaRNACall=""
callID=""
withED=false

# Handling input
while getopts "h?b:i:o:a:c:e" opt; do
    case "$opt" in
    h|\?)
        exit 0
        ;;
    b)  intaRNAbinary=$OPTARG
        ;;
    i)  inputPath=$OPTARG
        ;;
    o)  outputPath=$OPTARG
        ;;
    a)  intaRNACall=$OPTARG
        ;;
    c)  callID=$OPTARG
        ;;
    e)  withED=true
        ;;
    esac
done

# Enforce callID
if [ "$callID" == "" ]
then
  echo "No callID specified. Please specify a callID using -c <callID>"
  exit;
fi

# handling intaRNA commandline arguments
if [ "$intaRNACall" != "" ]
then
  intaRNACall="-a $intaRNACall"
fi

# Run benchmark
if [ "$withED" == true ]
then
  python bin/calls.py -b $intaRNAbinary -i $inputPath -o $outputPath -c $callID $intaRNACall -e -n
else
  python bin/calls.py -b $intaRNAbinary -i $inputPath -o $outputPath -c $callID $intaRNACall -n
fi

