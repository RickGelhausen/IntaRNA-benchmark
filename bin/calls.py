#!/usr/bin/python
# Author: Rick Gelhausen
import sys, getopt
import argparse
import os
import glob
from subprocess import Popen
from subprocess import PIPE

########################################################################################################################
#                                                                                                                      #
#            This script calls intaRNA with custom parameters on a set of sRNA queries and mRNA targets.               #
#            The script requires a callID to identify the call and to allow parallel runs of the script.               #
#                   The benchmark.py script is called after building the result files.                                 #
#                                                                                                                      #
########################################################################################################################

# Run a subprocess with the given call
def runSubprocess(call_, outputPath):
    with Popen(call_, shell=True, stdout=PIPE) as process:
        sys.stdout = open(outputPath, "w")
        print(str(process.stdout.read(),"utf-8"))
        sys.stdout = sys.__stdout__
        ru = os.wait4(process.pid, 0)[2]
        # Return time and memory usage
    return ru.ru_utime, ru.ru_maxrss


def main(argv):
    parser = argparse.ArgumentParser(description="Call script for benchmarking IntaRNA")
    parser.add_argument("-i", "--ifile", action="store", dest="intaRNAPath", default=os.path.join("..", "..", "IntaRNA", "src", "bin", ""),help="path where the intaRNA executable lies. Default: ../../IntaRNA/src/bin .")
    parser.add_argument("-o", "--ofile", action="store", dest="outputPath", default=os.path.join("..", "output"),help="output folder.")
    parser.add_argument("-f", "--ffile", action="store", dest="inputPath", default=os.path.join("..", "input"),help="input folder containing the fasta files required. Default: ./input")
    parser.add_argument("-a", "--arg", nargs="*", dest="commandLineArguments", default=[],help="command line arguments applied to the intaRNA query."
                                                                                               "Please use ** instead of -- (*/-) to avoid parser confusions.")
    parser.add_argument("-c", "--callID", action="store", dest="callID", default="",help="mandatory callID used to identify call.")
    args = parser.parse_args()

    if args.callID == "":
        sys.exit("No callID was specified! Please specify a callID using -c <name> or --callID=<name>")

    # Check whether intaRNA path exists
    if not os.path.exists(args.intaRNAPath):
        sys.exit("Error!!! IntaRNA filePath does not exist! Please specify it using python3 calls.py -i <intaRNApath>!")

    # Create outputFolder for this callID if not existing
    if not os.path.exists(os.path.join(args.outputPath, args.callID)):
        os.makedirs(os.path.join(args.outputPath, args.callID))
    else:
        sys.exit("Error!!! A directory for callID %s already exists!" % args.callID)

    # Organisms
    organisms = [x.split(os.path.sep)[-1] for x in glob.glob(os.path.join(args.inputPath,"*")) if os.path.isdir(x)]
    if organisms == []:
        sys.exit("Input folder is empty!")

    # Handle commandLineArguments for IntaRNA
    if args.commandLineArguments != []:
        cmdLineArguments = " ".join(args.commandLineArguments)
        cmdLineArguments = cmdLineArguments.replace("*","-")

    # Filepaths
    callLogFilePath = os.path.join(args.outputPath, args.callID, "calls.txt")
    timeLogFilePath = os.path.join(args.outputPath, args.callID, "runTime.csv")
    memoryLogFilePath = os.path.join(args.outputPath, args.callID, "memoryUsage.csv")

    for organism in organisms:
        # check if query and target folder exist
        if not os.path.exists(os.path.join(args.inputPath, organism, "query")):
            sys.exit("Error!!! Could not find query path for %s!" % organism)
        if not os.path.exists(os.path.join(args.inputPath, organism, "target")):
            sys.exit("Error!!! Could not find target path for %s!" % organism)

        fastaFileEndings = [".fasta", ".fa"]

        srna_files = []
        target_files = []
        for ending in fastaFileEndings:
            srna_files.extend(glob.glob(os.path.join(args.inputPath, organism, "query", "*" + ending)))
            target_files.extend(glob.glob(os.path.join(args.inputPath, organism, "target", "*" + ending)))

        # Sort input
        srna_files.sort()
        target_files.sort()

        # Check whether input exists
        if len(srna_files) == 0:
            sys.exit("Error!!! No srna fasta files found in query folder!")
        if len(target_files) == 0:
            sys.exit("Error!!! No target fasta files found in target folder!")


        for target_file in target_files:
            target_name = target_file.split(os.path.sep)[-1].split(".")[0]
            # Variables to create the timeLog table
            header = "callID;target_name;Organism"
            timeLine = "%s;%s;%s" % (args.callID, target_name, organism)
            memoryLine = "%s;%s;%s" % (args.callID, target_name, organism)

            for srna_file in srna_files:
                srna_name = srna_file.split(os.path.sep)[-1].split("_")[0]
                header += ";%s" % srna_name

                # Adding column
                timeLine += ";"
                memoryLine += ";"

                # IntaRNA call
                call = args.intaRNAPath + "IntaRNA" + " -q " + srna_file \
                                               + " -t " + target_file \
                                               + " --out=stdout --outMode=C "  \
                                               + cmdLineArguments
                print(call)
                print("%s\n" % call, file=open(callLogFilePath,"a"))

                # Outputfilepath
                out = os.path.join(args.outputPath, args.callID, srna_name + "_" + target_name + ".csv")

                # record time in seconds and memory in KB of this call
                timeCall, maxMemory = runSubprocess(call, out)

                # Time in seconds
                timeLine += "%.2f" % timeCall
                # Convert to megabyte (MB)
                memoryLine += "%.2f" % (float(maxMemory) / 1000)

            # print header if file is empty
            if not os.path.exists(timeLogFilePath):
                print(header, file=open(timeLogFilePath, "a"))
            if not os.path.exists(memoryLogFilePath):
                print(header, file=open(memoryLogFilePath, "a"))
            print(timeLine, file=open(timeLogFilePath, "a"))
            print(memoryLine, file=open(memoryLogFilePath, "a"))



    # Start benchmarking for this callID
    callBenchmark = "python3 benchmark.py -b %s" % (args.callID)
    with Popen(callBenchmark, shell=True, stdout=PIPE) as process:
        print(str(process.stdout.read(), "utf-8"))

if __name__ == "__main__":
   main(sys.argv[1:])
