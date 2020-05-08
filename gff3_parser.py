#! /usr/bin/env python
import sys
from Bio.Seq import Seq
from Bio.Alphabet import IUPAC
import gzip
import argparse
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
    #parser.add_argument("-t",help="Number of Cores",action="store",dest="threads",type=int, default=-1, required=False)
    args = parser.parse_args()
    if not os.path.isfile(args.gff):
        print args.gff, "is not a correct file path!"
        sys.exit()
    if not os.path.isfile(args.fasta):
        print args.fasta, "is not a correct file path!"
        sys.exit()

    return args

def readGFF(output, gff, allSeq):
    '''    
    Reads the gff3 file and extracts CDS regions
    Input: gff3 file and dictionary of all sequences

    '''
    input = ""
    if gff[-3:]=='.gz':
        input = gzip.open(gff,'r')
    else:
        input = open(gff,'r')
    currentAccession = ""
    currentGene = ""
    currentSeq = ""
    lastBadAccession = ""
    afterFirst=False
    for line in input:
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
                    output.write("\n")
                afterFirst = True
                
                output.write('>'+info[8]+'\n')
                currentAccession = accession
                currentSeq = allSeq[accession]
            if accession != currentAccession:
                lastBadAccession = accession
                continue
        smaller = currentSeq[int(info[3])-1:int(info[4])]
        if len(smaller) ==0:
            print 'a'
            continue
        if info[6] == '-':
            my_seq = Seq(smaller)
            output.write(str(my_seq.reverse_complement())+'*')
        else:
            output.write(smaller+'*')
    output.write("\n")    
    output.close()
    input.close()    


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
        
        if line[0] =='>':
            if sequenceLine !="":
                allSeq[lastHeader] = sequenceLine
            if line.startswith('>gi'):
                if line.count('|')>=3:
                    lastHeader = line.split("|")[3]
                else:
                    lastHeader= line[1:].strip()
            else:
                if line.count('|')>=1:
                    lastHeader = line.split("|")[1]
                elif line.count(' ')>0:
                    lastHeader = line.split(" ")[0][1:]
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
        output = open(args.output,'w')
    readGFF(output,args.gff,sequences)

