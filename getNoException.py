#! /usr/bin/env python
import sys

#also gets the longest isoform
input = open(sys.argv[1],'r')
output = open(sys.argv[2],'w')

header = ''
geneName = ''
countTotal = 0
goodHeader = False
bestGenes = dict()
for line in input:
	line = line.strip()
	if goodHeader:
		if 'Error' in line:
			goodHeader=False
			continue
		else:
			countTotal +=1
			
			if geneName in bestGenes:
				if len(bestGenes[geneName][1])<len(line):
					bestGenes[geneName][0] = header
					bestGenes[geneName][1] = line
			else:
				bestGenes[geneName] = []
				bestGenes[geneName].append(header)
				bestGenes[geneName].append(line)

			#output.write(header + line)
			header = ""
			if countTotal ==1:#65:
				goodHeader=False
				countTotal = 0
	elif line[0] == '>':
		if 'exception' in line:
			continue
		if 'transl_except' in line:
			continue
		if 'partial=true' in line:
			continue
		if "gene=" in line:
			geneName = line.split("gene=")[1].split(";")[0]
		else:
			geneName = line
		header=line
		goodHeader = True
		countTotal = 0



for key in bestGenes:
	for line in bestGenes[key]:
		output.write(line + "\n")

input.close()
output.close()

