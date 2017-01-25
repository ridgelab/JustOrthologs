#! /usr/bin/env python
import sys
from multiprocessing import Process, current_process, freeze_support, Pool
import argparse
import os

def getCor(largeList,smallList,totalCor,looser):
	GLOBAL_BEST_COR = 0.05
	if looser:
		GLOBAL_BEST_COR = 0.1
	for pos in range(len(smallList)-1):
		numberPosDoneSoFar = 0
		bestCor = GLOBAL_BEST_COR
		for otherPos in range(len(largeList)-1): 
			if len(largeList[otherPos]) != len(smallList[pos]):
				continue
			if (len(smallList[pos])<15) or (len(largeList[otherPos])<15):
				continue
			A =   abs(float((smallList[pos].count("AA"))/float(len(smallList[pos]))) - (float(largeList[otherPos].count("AA"))/float(len(largeList[otherPos]))))
			A1 =  abs(float((smallList[pos].count("AT"))/float(len(smallList[pos]))) - (float(largeList[otherPos].count("AT"))/float(len(largeList[otherPos]))))
			A2 =  abs(float((smallList[pos].count("AC"))/float(len(smallList[pos]))) - (float(largeList[otherPos].count("AC"))/float(len(largeList[otherPos]))))
			A3 =  abs(float((smallList[pos].count("AG"))/float(len(smallList[pos]))) - (float(largeList[otherPos].count("AG"))/float(len(largeList[otherPos]))))
			A4 =  abs(float((smallList[pos].count("TA"))/float(len(smallList[pos]))) - (float(largeList[otherPos].count("TA"))/float(len(largeList[otherPos]))))
			A5 =  abs(float((smallList[pos].count("TT"))/float(len(smallList[pos]))) - (float(largeList[otherPos].count("TT"))/float(len(largeList[otherPos]))))
			A6 =  abs(float((smallList[pos].count("TC"))/float(len(smallList[pos]))) - (float(largeList[otherPos].count("TC"))/float(len(largeList[otherPos]))))
			A7 =  abs(float((smallList[pos].count("TG"))/float(len(smallList[pos]))) - (float(largeList[otherPos].count("TG"))/float(len(largeList[otherPos]))))
			A8 =  abs(float((smallList[pos].count("CA"))/float(len(smallList[pos]))) - (float(largeList[otherPos].count("CA"))/float(len(largeList[otherPos]))))
			A9 =  abs(float((smallList[pos].count("CT"))/float(len(smallList[pos]))) - (float(largeList[otherPos].count("CT"))/float(len(largeList[otherPos]))))
			A0 =  abs(float((smallList[pos].count("CC"))/float(len(smallList[pos]))) - (float(largeList[otherPos].count("CC"))/float(len(largeList[otherPos]))))
			A11 = abs(float((smallList[pos].count("CG"))/float(len(smallList[pos]))) - (float(largeList[otherPos].count("CG"))/float(len(largeList[otherPos]))))
			A12 = abs(float((smallList[pos].count("GA"))/float(len(smallList[pos]))) - (float(largeList[otherPos].count("GA"))/float(len(largeList[otherPos]))))
			A13 = abs(float((smallList[pos].count("GT"))/float(len(smallList[pos]))) - (float(largeList[otherPos].count("GT"))/float(len(largeList[otherPos]))))
			A14 = abs(float((smallList[pos].count("GC"))/float(len(smallList[pos]))) - (float(largeList[otherPos].count("GC"))/float(len(largeList[otherPos]))))
			A15 = abs(float((smallList[pos].count("GG"))/float(len(smallList[pos]))) - (float(largeList[otherPos].count("GG"))/float(len(largeList[otherPos]))))
			if looser:
				cor = -2.2
				cor = cor +float(A +A1 +A2 +A3 +A4 +A5 +A6 +A7 +A8 + A9+ A0 +A11 +A12 +A13 +A14 + A15)
				sortList = []
				sortList.append(A)
				sortList.append(A1)
				sortList.append(A2)
				sortList.append(A3)
				sortList.append(A4)
				sortList.append(A5)
				sortList.append(A6)
				sortList.append(A7)
				sortList.append(A8)
				sortList.append(A9)
				sortList.append(A0)
				sortList.append(A11)
				sortList.append(A12)
				sortList.append(A13)
				sortList.append(A14)
				sortList.append(A15)
				sortList = sorted(sortList)
				if sortList[-1] <0.03:	
					bestCor = cor
				continue
			cor = float(A +A1 +A2 +A3 +A4 +A5 +A6 +A7 +A8 + A9+ A0 +A11 +A12 +A13 +A14 + A15)
			if cor< bestCor:
				bestCor = cor
		if bestCor<GLOBAL_BEST_COR:
			totalCor += bestCor
			continue
		if looser:
			totalCor +=1
			continue
		totalCor+=2 
	return totalCor

def readFile2(input2,info,BSSF,looser):
	in2 = open(input2,'r')
	smallestStringSize = len(info)-1
	bestOrthologHeader = ""
	bestOrthNum = -1
	numSeen =0	
	for otherLine in in2:
		totalCor = 0
		if otherLine[0] == '>':
			otherHeader = otherLine
			continue
		numSeen +=1
		info2 = otherLine.strip().split("*")
		smallList = []
		largeList = []
		smallestStringSize = len(info)-1
		if (len(info2)-1)<(len(info)-1):
			smallestStringSize = len(info2)-1
			smallList = info2
			largeList = info
		else:
			smallList = info
			largeList = info2
		maxNumSkipped = len(smallList)/5
		if maxNumSkipped<3:
			maxNumSkipped=(len(smallList)-1)/2
		if (len(info2)-len(info))>(maxNumSkipped+1):
			break
		totalCor = (2*abs(len(info)-len(info2)))
		totalCor = getCor(largeList,smallList,totalCor,looser)
		if totalCor<BSSF:
			BSSF =totalCor
			bestOrthologHeader = otherHeader
			bestOrthNum = numSeen
		elif type(BSSF) == int:
			if type(totalCor)==float:
				BSSF =totalCor
				bestOrthologHeader = otherHeader
				bestOrthNum = numSeen
	in2.close()
	return BSSF,bestOrthologHeader

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
					keys.add(line) #lastLine
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
				####DONE###Add if statement here too.
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
		temp5 = combineFiles(temp1,temp2,"") ##I'm working on this part
		temp6 = combineFiles(temp3,temp4,"")
		output = open(outputFile,'w')
		output.write("Ortholog Group\t" + inputFile + "\t" + input2File +"\n")
		combineFiles2(temp5,temp6,output)
	else:
		output = open(outputFile,'w')
		output.write("Ortholog Group\t" + inputFile + "\t" + input2File+"\n")
		combineFiles(temp1,temp2,output)
	
