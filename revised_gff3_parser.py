#! /usr/bin/env python
import sys
from Bio.Seq import Seq
from Bio.Alphabet import IUPAC
import gzip
import argparse


zippedGFF3 =False
zippedRef =False
if sys.argv[1][-3:] =='.gz':
	zippedGFF3 = True
if sys.argv[2][-3:] =='.gz':
	zippedRef = True

input = ""
allDNA = ""
if zippedGFF3:
	input = gzip.open(sys.argv[1],'r')
else:
	input = open(sys.argv[1],'r')
if zippedRef:
	allDNA = gzip.open(sys.argv[2],'r')
else:
	allDNA = open(sys.argv[2],'r')
output = open(sys.argv[3],'w')


allStartPos = dict()

lastHeader = ""
sequenceLine = ""
for line in allDNA:
	
	if line[0] =='>':
		if sequenceLine !="":
			allStartPos[lastHeader] = sequenceLine
		lastHeader = line
		sequenceLine = ""
		continue
	sequenceLine +=line.strip()


allDNA.close()
if sequenceLine !="":
	allStartPos[lastHeader] = sequenceLine

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
		for key in allStartPos.keys():
			if accession in key:
				if afterFirst:
					output.write("\n")
				afterFirst = True
				
				output.write('>'+info[8]+'\n')
				if accession !=currentAccession:
					currentAccession = accession
					currentSeq = allStartPos[key]
					break
		if accession != currentAccession:
			lastBadAccession = accession
			continue

	if info[6] == '-':
		smaller = currentSeq[int(info[3])-1:int(info[4])]
		my_seq = Seq(smaller)
		output.write(str(my_seq.reverse_complement())+'*')
	else:
		output.write(currentSeq[int(info[3]) -1:int(info[4])]+'*')
		
output.write("\n")	
output.close()
input.close()	
