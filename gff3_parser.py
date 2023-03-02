#! /usr/bin/env python 3
import sys
import gzip
import argparse
from Bio.Seq import Seq
#from multiprocessing import Process, current_process, freeze_support, Pool
#Multiproccessing is not necessary because the program is fast. 
#However, if it were to be implemented, the commented out lines would probably be necessary.
def parseArgs():
    '''
    Parses arguments. A gff3 file and fasta file are required. 
    An output file is optional. If an output file is not specified, output will be writted to standard out.
    '''
    import os
    parser = argparse.ArgumentParser(description='Find Orthologs in Two Files.')
    parser.add_argument("-g",help="Input GFF3 file",action="store", dest="gff", required=True)
    parser.add_argument("-f",help="Input Fasta File",action="store",dest="fasta", required=True)
    parser.add_argument("-o",help="Output File",action="store",dest="output", required=False)
    parser.add_argument("-z",help="Gzip Output File",action="store_true",dest="gzip", required=False)
    #parser.add_argument("-t",help="Number of Cores",action="store",dest="threads",type=int, default=-1, required=False)
    args = parser.parse_args()
    if not os.path.isfile(args.gff):
        print (args.gff, "is not a correct file path!")
        sys.exit()
    if not os.path.isfile(args.fasta):
        print (args.fasta, "is not a correct file path!")
        sys.exit()

    return args

def readGFF(output, gff, allSeq,args):
    '''    
    Reads the gff3 file and extracts CDS regions
    Input: gff3 file and dictionary of all sequences

    '''
    inputF = ""
    if gff[-3:]=='.gz':
        inputF = gzip.open(gff,'r')
    else:
        inputF = open(gff,'r')
    currentAccession = ""
    currentGene = ""
    currentSeq = ""
    lastBadAccession = ""
    afterFirst=False
    for line in inputF:
        if isinstance(line,bytes):
            line = line.decode('UTF-8')
        if line[0]=='#':
            continue
        info = line.strip().split("\t")
        if info[2] != "CDS":
            continue
        accession = info[0]
        if accession ==lastBadAccession:
            continue
        gene = info[8]
        if gene !=currentGene:
            currentGene = gene
            if accession in allSeq:
                if afterFirst:
                    if args.gzip:
                        output.write(b'\n')
                    else:
                        output.write('\n')
                afterFirst = True
                
                if args.gzip:
                    output.write(('>'+info[8]+'\n').encode())
                else:
                    output.write('>'+info[8]+'\n')
                currentAccession = accession
                currentSeq = allSeq[accession]
            if accession != currentAccession:
                lastBadAccession = accession
                continue
        smaller = currentSeq[int(info[3])-1:int(info[4])]
        if len(smaller) ==0:
            print ('Sequence length is zero')
            continue
        if info[6] == '-':
            my_seq = Seq(smaller)
            if args.gzip:
                output.write(str(my_seq.reverse_complement()).encode()+b'*')
            else:
                output.write(str(my_seq.reverse_complement())+'*')
        else:
            if args.gzip:
                output.write(smaller.encode()+b'*')
            else:
                output.write(smaller+'*')
    
    if args.gzip:
        output.write(b"\n")    
    else:
        output.write("\n")    

    output.close()
    inputF.close()    


def readFasta(fasta):
    '''
    Reads a fasta file and returns a dictionary where the key is the accession number and the value is the sequence.
    Input: path to a fasta file
    Returns: Dictionary of fasta file sequences.
    '''
    allDNA = ""
    if fasta[-3:]=='.gz':
        allDNA = gzip.open(fasta,'r')
    else:
        allDNA = open(fasta,'r')
    allSeq = dict()
    lastHeader = ""
    sequenceLine = ""
    for line in allDNA:
        if isinstance(line,bytes):
            line = line.decode('UTF-8')
        
        if line[0] =='>':
            if sequenceLine !="":
                allSeq[lastHeader] = sequenceLine
            if line.count('|')>=3:
                lastHeader = line.split("|")[3]
            elif line.count(' ')>=2:
                lastHeader = line.split(" ")[0][1:]
            elif line.count('\t')>=2:
                lastHeader = line.split("\t")[0][1:]
            else:
                lastHeader= line[1:].strip()
            sequenceLine = ""
            continue
        sequenceLine +=line.strip()
    allDNA.close()
    if sequenceLine !="":
        allSeq[lastHeader] = sequenceLine
    return allSeq

if __name__ =='__main__':
    '''
    Main
    '''
    #freeze_support()
    args = parseArgs()
    sequences = readFasta(args.fasta)
    output = sys.stdout
    if args.output:
        if args.gzip:
            outputFile = args.output
            if not outputFile.endswith(".gz"):
                outputFile += ".gz"
            output = gzip.open(outputFile,'w')
        else:
            output = open(args.output,'w')
    readGFF(output,args.gff,sequences,args)

