#! /usr/bin/env python
import sys
import argparse
'''
This program is used for determining orthologous groups between multiple output files from justOrthologs.
It compares the orthologs found in a Species A vs Species B with the ortholog found in Species B with
Species C. If Species C has an ortholog with Species A, and that ortholog is not the same as the original
ortholog, then the ortho group is not reported.
'''


def parseArgs():
	'''
	Parses arguments. The input files must be output from JustOrthologs. The input directory (if used) must only include output
	files from JustOrthologs. The output file path is optional. If not used, output will be written to standard out.
	The number of cores is optional. By default, all available threads are used.
	'''
	parser = argparse.ArgumentParser(description='Find Orthologs in Two Files.')
	parser.add_argument("-i",help="Input Fasta Files",nargs='*',action="store", dest="input", required=False)
	parser.add_argument("-id",help="Input Directory with JustOrthologs output files",action="store", dest="inputDir", required=False)
	parser.add_argument("-o",help="outputFilePath",action="store",dest="output", required=False)
	args =parser.parse_args()

	return args


def readInputFiles(args):
	'''
	Input: System arguments
	Output: List of paths ot all JustOrthologs output files
	'''
	import os
	allSpecies = []
	if args.input:
		allSpecies = args.input
	elif args.inputDir:
	
		path = args.inputDir
		allSpecies1 = os.listdir(path)
		if path[-1] != '/':
			path += '/'
		allSpecies = [path +i for i in allSpecies1]
	else:
		print "You must supply input files or an input directory."
		sys.exit()
	return allSpecies


def findOrthoGroup(allOrthologs,key,speciesUsed,allOrthos):
	'''
	Recursive method which identifies all orthologous genes belonging to a specific group.
	Input: A dictionary with the key being a gene name and the value is a set of all genes which have been identified (by this algorithm) as being orthologous to that gene.
		A gene (belonging to the group)
		Species which have already been included
		Orthologs that have already been identified
	Returns: A set of all orthologs pertaining to that gene. 
		If more than one gene is identified from a species, and empty set is returned.
	'''

	for oKey in allOrthologs[key]:
		if oKey in allOrthos:
			continue
		if len(allOrthos)==0:
			return allOrthos
		species = oKey.split(':')[0]
		if species in speciesUsed:
			allOrthos = set()
			return allOrthos
		speciesUsed.add(species)
		allOrthos.add(oKey)
		allOrthos = findOrthoGroup(allOrthologs,oKey,speciesUsed,allOrthos)
		if len(allOrthos)==0:
			return allOrthos
	return allOrthos

def addToDict(species, allOrthologs):
	'''
	Input: Path to a JustOrthologs output file for a species and a dictionary with the key being a gene name and the value is a set of all genes which have
		been identified (by this algorithm) as being orthologous to that gene.
	Returns: A dictionary with the key being a gene name and the value is a set of all genes which have been identified (by this algorithm) as being orthologous to that gene.
	'''
	input = open(species,'r')
	bothSpecies = input.next().strip().split("\t")
	if len(bothSpecies)!=3:
		return allOrthologs
	spec2 = bothSpecies[1].split('/')[-1]
	spec1 = bothSpecies[2].split('/')[-1]
	#spec1 = bothSpecies[1].split('/')[-1]
	#spec2 = bothSpecies[2].split('/')[-1]
	for line in input:
		line = line.strip()
		bothGenes = line.split("\t")
		if len(bothGenes) !=3:
			continue
		gene1 = spec1 + ":" + bothGenes[1]
		if ";Name=" in gene1:
			gene1 = spec1 + ":" + bothGenes[1].split(";Name=")[1].split(";")[0]
		gene2 = spec2 + ":" + bothGenes[2]
		if ";Name=" in gene2:
			gene2 = spec2 + ":" + bothGenes[2].split(";Name=")[1].split(";")[0]
		if "gene=" in bothGenes[1]:
			gene1 = gene1 +"(" +bothGenes[1].split("gene=")[1].split(";")[0] +")"
		if "gene=" in bothGenes[2]:
			gene2 = gene2 +"(" +bothGenes[2].split("gene=")[1].split(";")[0] +")"
		if not gene1 in allOrthologs:
			allOrthologs[gene1] = set()
		mySet = allOrthologs[gene1]
		mySet.add(gene1)
		mySet.add(gene2)
		allOrthologs[gene1] = mySet
		if not gene2 in allOrthologs:
			allOrthologs[gene2] = set()
		mySet2 = allOrthologs[gene2]
		mySet2.add(gene1)
		mySet2.add(gene2)
		allOrthologs[gene2] = mySet2
	input.close()	
	return allOrthologs

def writeToFile(args,allOrthologs):
	'''
	Input: System arguments and a dictionary with the key being a gene name and the value is a set of all genes which have been identified (by this algorithm) as being orthologous to that gene.
	Output: None
	'''

	output = sys.stdout
	usedGenes = set()
	groupNum =0
	if args.output:
		output = open(args.output,'w')
	for key in allOrthologs:
		if key in usedGenes:
			continue
		spec = key.split(":")[0]
		speciesUsed = set()
		speciesUsed.add(spec)
		allOrthos = set()
		allOrthos.add(key)
		allOrthos = findOrthoGroup(allOrthologs,key,speciesUsed,allOrthos)
		if len(allOrthos)>0:
			groupNum +=1
			output.write("Ortholog Group " + str(groupNum) + ":")
			for x in allOrthos:	
				usedGenes.add(x)
				output.write("\t" + x)
			output.write("\n")
	if args.output:
		output.close()


if __name__ =='__main__':
	'''
	Main
	'''
	args = parseArgs()
	sys.setrecursionlimit(9999999)
	allSpecies = readInputFiles(args)
	allOrthologs = dict()
	for species in allSpecies:
		allOrthologs = addToDict(species,allOrthologs)
	writeToFile(args,allOrthologs)


