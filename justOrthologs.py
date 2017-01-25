#! /usr/bin/env python
import sys
from multiprocessing import Process, current_process, freeze_support, Pool
import argparse
import os
from getCor import getCor, readFile2


def searchOtherFile(inputStuff):
	header,line,input2,looser = inputStuff
	info = line.strip().split("*")
	GLOBAL_BSSF = 2*(len(info)-1)
	if looser:
		if len(info)<6:
			GLOBAL_BSSF = -2.15
		else:
			GLOBAL_BSSF = 0
	BSSF = GLOBAL_BSSF
	BSSF,bestOrthologHeader=readFile2(input2,info,BSSF,looser)
	if type(BSSF) == int:
		return ""
	if BSSF <GLOBAL_BSSF:
		return (str(BSSF),header,bestOrthologHeader)
	return ""

def parseArgs():
	parser = argparse.ArgumentParser(description='Find Orthologs in Two Files.')
	parser.add_argument("-q",help="Query Fasta File",action="store", dest="query", required=True)
	parser.add_argument("-s",help="Subject Fasta File",action="store",dest="subject", required=True)
	parser.add_argument("-o",help="Output File",action="store",dest="output", required=True)
	parser.add_argument("-t",help="Number of Cores",action="store",dest="threads",type=int, required=False)
	parser.add_argument("-d",help="For More Distantly Related Species",action="store_true",dest="distant", required=False)
	parser.add_argument("-c",help="Combine Both Algorithms For Best Accuracy",action="store_true",dest="combine", required=False)
	args = parser.parse_args()
	threads =16
	if args.threads:
		threads = args.threads 
	if not os.path.isfile(args.subject):
		print args.subject, "is not a correct file path!"
		sys.exit()
	if not os.path.isfile(args.query):
		print args.query, "is not a correct file path!"
		sys.exit()
	looser =False
	if args.distant:
		looser = True
	both = False
	if looser and args.combine:
		parser.error("--c cannot be used with --d")
		sys.exit()
	if args.combine:
		both = True
	return args.subject,args.output,args.query,threads,looser,both

def callFindOrthologs(inputFile,input2File,threads,looser):
	input = open(inputFile,'r')
	pool = Pool(threads)
	header = ""
	tasks = []
	inQueue = 0
	for line in input:
		if line[0] == '>':
			header = line
			continue
		tasks.append((header,line,input2File,looser))
	temp = pool.map(searchOtherFile,tasks,chunksize=1)
	input.close()
	return temp

def combineFiles(input,in2,output):
	keys = set()
	lineDict = dict()
	lastLine = ""
	for info in input:
		if info != "":
			line = info[1]
			lastLine = info[2]
			keys.add(lastLine)
			lineDict[line] = lastLine
			lineDict[lastLine] = line
	lastLine = ""
	badOnes = set()
	for info in in2:

		if info!= "":
			line = info[1]
			lastLine = info[2]
			if line in lineDict:
				if lineDict[line] ==lastLine:
					continue
				else:
					if line in keys:
						keys.remove(line)
						badOnes.add(line)
					if lastLine in keys:
						keys.remove(lastLine)
						badOnes.add(lastLine)
					if lineDict[line] in keys:
						badOnes.add(lineDict[line])
						keys.remove(lineDict[line])
					if lastLine in lineDict:
						if lineDict[lastLine] in keys:
							badOnes.add(lastLine)
							keys.remove(lineDict[lastLine])
					continue
			elif lastLine in lineDict:
				if lineDict[lastLine] ==line:
					continue
				else:
					if lastLine in keys:
						keys.remove(lastLine)
						badOnes.add(lastLine)
					if line in keys:
						badOnes.add(line)
						keys.remove(line)
					if lineDict[lastLine] in keys:
						badOnes.add(lineDict[lastLine])
						keys.remove(lineDict[lastLine])
					if line in lineDict:
						if lineDict[line] in keys:
							badOnes.add(lineDict[line])
							keys.remove(lineDict[line])
					continue
			else:
				if not line in badOnes and not lastLine in badOnes:
					keys.add(line) 
					lineDict[line] = lastLine
					lineDict[lastLine] = line
	currentOrtho = 1
	returnOrthologs = []

	if output == '':
		for key in keys:
			returnOrthologs.append((str(currentOrtho),key.strip(),lineDict[key]))
			currentOrtho +=1
		return returnOrthologs
	else:
		for key in keys:
			output.write("Ortholog Group " + str(currentOrtho) + ":\t" +key.strip() +"\t" +lineDict[key])
			currentOrtho +=1


def combineFiles2(input,in2,output):
	lineDict = dict()
	keysInDict = set()
	for info in input:
		line2 = info[1] 
		keysInDict.add(line2)
		lastLine = info[2].strip()
		lineDict[line2] = lastLine
		lineDict[lastLine] = line2
	for info in in2:
		line2 = info[1]
		lastLine = info[2].strip()
		if line2 in lineDict.keys():
			if lineDict[line2] ==lastLine:
				lastLine = ""
				continue
			else:
				if lineDict[line2] in lineDict:
					del lineDict[lineDict[line2]]
				del lineDict[line2]
				keysInDict.remove(line2)
				lastLine = ""
				continue
		elif lastLine in lineDict.keys():
			if lineDict[lastLine] ==line2:
				lastLine = ""
				continue
			else:
				keysInDict.remove(lineDict[lastLine])
				if lineDict[lastLine] in lineDict:
					del lineDict[lineDict[lastLine]]
				del lineDict[lastLine]
				lastLine = ""
				continue
		lineDict[line2] = lastLine
		lineDict[lastLine] = line2
		keysInDict.add(line2)
	groupNum = 1
	keys = set()
	for key in keysInDict:
		if key in keys:
			continue
		keys.add(lineDict[key])
		output.write("Ortholog Group "+str(groupNum) + ":\t" +key +"\t" +lineDict[key] +"\n")
		groupNum +=1
	output.close()

if __name__ =='__main__':
	freeze_support()
	inputFile,outputFile,input2File,threads,looser,both = parseArgs()
	temp1 = callFindOrthologs(inputFile,input2File,threads,looser)
	temp2 = callFindOrthologs(input2File,inputFile,threads,looser)
	if both:
		looser = True
		temp3 = callFindOrthologs(inputFile,input2File,threads,looser)
		temp4 = callFindOrthologs(input2File,inputFile,threads,looser)
		temp5 = combineFiles(temp1,temp2,"") 
		temp6 = combineFiles(temp3,temp4,"")
		output = open(outputFile,'w')
		output.write("Ortholog Group\t" + inputFile + "\t" + input2File +"\n")
		combineFiles2(temp5,temp6,output)
	else:
		output = open(outputFile,'w')
		output.write("Ortholog Group\t" + inputFile + "\t" + input2File+"\n")
		combineFiles(temp1,temp2,output)
	
