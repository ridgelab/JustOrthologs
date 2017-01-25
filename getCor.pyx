#! /usr/bin/env python



def getCor(largeList,smallList,totalCor,looser):
	cdef float GLOBAL_BEST_COR, bestCor, A,A1,A2,A3,A4,A5,A6,A7,A8,A9,A10,A11,A12,A13,A14,A15,cor
	GLOBAL_BEST_COR = 0.05
	if looser:
		GLOBAL_BEST_COR = 0.1
	for pos in range(len(smallList)-1):
		bestCor = GLOBAL_BEST_COR
		for otherPos in xrange(len(largeList)-1): 
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
				cor += float(A +A1 +A2 +A3 +A4 +A5 +A6 +A7 +A8 + A9+ A0 +A11 +A12 +A13 +A14 + A15)
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

largeList = []
smallList = []
totalCor = 12
looser = True
getCor(largeList,smallList,totalCor,looser)

def readFile2(input2,info,BSSF,looser):
	cdef int smallestStringSize, bestOrthNum,numSeen
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
	return (BSSF,bestOrthologHeader)


