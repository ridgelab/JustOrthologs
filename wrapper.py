#! /usr/bin/env python2
import sys
import argparse
import os
import subprocess

TEMP_FILE_NUM = ""
def checkTempNum(TEMP_FILE_NUM):
    '''
    Ensures that the same temporary file is used.
    '''
    for fname in os.listdir('.'):
        if fname.endswith(TEMP_FILE_NUM):
            return True
    return False

def parseArgs():
    '''
    Parse arguments.
    '''
    parser = argparse.ArgumentParser(description='Provides a variety of tools which allows you to\n'  \
            +'1.\tExtract CDS regions from a reference genome and fasta file\n' \
            +'2.\tFilter genes by choosing the longest isoform and ing filters based on annotations\n' \
            +'3.\tSort genes based on the number of CDS regions\n' \
            +'4.\tRun JustOrthologs (an ortholog finding algorithm) between two species')
    
    parser.add_argument("-g1",help="1st GFF3 (gzip allowed with .gz)",action="store", dest="gff3_One", required=False)
    parser.add_argument("-g2",help="2nd GFF3 fasta file (gzip allowed with .gz)",action="store", dest="gff3_Two", required=False)
    parser.add_argument("-r1",help="1st Reference Genome (gzip allowed with .gz)",action="store",dest="ref_One", required=False)
    parser.add_argument("-r2",help="2nd Reference Genome (gzip allowed with .gz)",action="store",dest="ref_Two", required=False)
    parser.add_argument("-fa1",help="1st Fasta file (only used without --e)",action="store", dest="fasta1", required=False)
    parser.add_argument("-fa2",help="2nd Fasta file (only used without --e)",action="store", dest="fasta2", required=False)
    parser.add_argument("-e",help="Extract CDS regions from genomes",action="store_true",dest="extract", required=False)
    parser.add_argument("-r",help="Run JustOrthologs",action="store_true",dest="run", required=False)
    parser.add_argument("-f",help="Filters genes based on annotations",action="store_true",dest="filter", required=False)
    parser.add_argument("-s",help="Sort FASTA file for running JustOrthologs",action="store_true",dest="sort", required=False)
    parser.add_argument("-k",help="Keep All Temporary Files",action="store_true",dest="keep", required=False)
    parser.add_argument("-d",help="For Distantly Related Species (only with --r)",action="store_true",dest="distant", required=False)
    parser.add_argument("-c",help="Combine Both Algorithms In JustOrthologs For Best Accuracy",action="store_true",dest="combine", required=False)
    parser.add_argument("-o",help="Output File for --r",action="store",dest="output", required=False)
    parser.add_argument("-t",help="Number of Cores (only affects -r option)",action="store",dest="threads",type=int, required=False)
    parser.add_argument("-all",help="Run --e, --f, --s, and --r",action="store_true",dest="run_all", required=False)
    args = parser.parse_args()

    if not any(vars(args).values()):
        parser.error("No Arguments given")
        sys.exit()
    
    if args.run_all:
        args.extract = True
        args.filter = True
        args.sort = True
        args.run = True

    if args.gff3_One and args.extract and args.ref_One is None:
        parser.error("--g1 with --e requires --r1")
        sys.exit()
    if args.ref_One and args.extract and args.gff3_One is None:
        parser.error("--r1 with --e requires --g1")
        sys.exit()
    if args.gff3_Two and args.extract and args.ref_Two is None:
        parser.error("--g2 with --e requires --r2")
        sys.exit()
    if args.ref_Two and args.extract and args.gff3_Two is None:
        parser.error("--r2 with --e requires --g2")
        sys.exit()
    if args.gff3_Two and args.extract and args.gff3_One is None:
        parser.error("--g2 with --e requires --g1")
        sys.exit()
    if args.extract and args.gff3_One is None:
        parser.error("--e requires --g1 (--g2 optional)")
        sys.exit()
    if args.filter and args.gff3_One is None and args.fasta1 is None:
        parser.error("--f requires --g1 (--g2 optional) or --fa")
        sys.exit()
    if args.sort and args.gff3_One is None and args.fasta1 is None:
        parser.error("--s requires --g1 (--g2 optional) or --fa")
        sys.exit()
    if args.run and ((args.fasta1 is None and args.fasta2 is None) and (args.ref_One is None or args.ref_Two is None)):
        parser.error("--r requires (--r1 and --r2) or (--fa1 and --fa2)")
        sys.exit()
    if args.run and args.output is None:
        parser.error("--r requires --o")
        sys.exit()
    if args.run and args.ref_One and not args.sort:
        parser.error("--r requires --s when used with --r1")
        sys.exit()
    if args.run and args.ref_One and not args.extract:
        parser.error("--r requires --e when used with --r1")
        sys.exit()
    if (args.fasta1 or args.fasta2) and (args.ref_One or args.ref_Two):
        parser.error("--fa1 and --fa2 cannot be run with --r1 or --r2")
        sys.exit()
    if args.fasta2 and args.fasta1 is None:
        parser.error("--fa2 requires --fa1")
        sys.exit()
    if args.fasta1 and args.fasta2 is None and not args.sort and not args.filter:
        parser.error("--fa1 without --fa2 requires --s or --f")
        sys.exit()
    if args.keep and args.fasta1 is None and args.ref_One is None:
        parser.error("--k requires an input file (--r1 or --fa1)")
        sys.exit()
    if args.distant and args.combine:
        parser.error("--c cannot be used with --d")
        sys.exit()
    if args.output and not args.run and not args.sort:
        print "Warning: Output file is only used when included with --r option or --s"
    if args.distant and not args.run:
        print "Warning: --d is only used when included with --r option"
    if args.combine and not args.run:
        print "Warning: --c is only used when included with --r option"
    if args.run and not args.sort:
        print "Warning: It is highly recommended that you use --s when running --r"

    possibleFiles = {'gff3_One','gff3_Two','ref_One','ref_Two','fasta'}
    count = 0
    for x in vars(args):
        count +=1
        if x in possibleFiles and vars(args)[x] is not None:
            file= str(vars(args)[x])
            if not os.path.isfile(file):
                print file, "is not a correct file path!"
                sys.exit()
    return args


def cleanUp(printFiles):
    '''
    Removes all temporary files.
    '''
    possibleFiles = {'.extract_1_'+ TEMP_FILE_NUM,'.extract_2_'+TEMP_FILE_NUM,'.filter_1_'+TEMP_FILE_NUM,'.filter_2_'+TEMP_FILE_NUM,'.sort_1_'+TEMP_FILE_NUM,'.sort_2_'+TEMP_FILE_NUM}

    for pos in possibleFiles:
        if printFiles:
            if os.path.isfile(pos):
                print "Temporary File is located at:",pos
        else:
            if os.path.isfile(pos):
                
                os.remove(pos)



def runExtract(gff3,ref,keep,num):
    '''
    Extracts coding sequences from gff3 files.
    '''
    try:
        temp1 = ".extract_" +str(num) +"_" + TEMP_FILE_NUM 
        command = ['python2', 'gff3_parser.py', '-g', gff3, '-f', ref, '-o', temp1]
        prog=  subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except Exception:
        print "Error Occurred in Extract"
        cleanUp(True)
        sys.exit()
    return prog,temp1
def runFilter(input, num):
    '''
    Ensures that all sequences have no annotated exceptions.
    '''
    try:
        temp1 = ".filter_" +str(num) +"_" + TEMP_FILE_NUM
        command = ['python2', 'getNoException.py', '-i', input, '-o', temp1]
        prog=  subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except Exception:
        print "Error Occurred in Filter"
        cleanUp(True)
        sys.exit()
    return prog,temp1
def runSort(input, fileName):
    '''
    Sorts the files based on number of CDS regions.
    '''
    try:
        command = ['bash', 'sortFastaBySeqLen.sh', input, fileName]
        prog=  subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except Exception:
        print "Error Occurred in Sort"
        cleanUp(True)
        sys.exit()
    return prog,fileName
def runJustOrthologs(query,subject,threads,output,distant, combine):
    '''
    Runs JustOrthologs
    '''
    output = output + TEMP_FILE_NUM
    try:
        command = None
        if distant:
            command = ['python2', 'justOrthologs.py', '-q', query,'-s',subject,'-t',threads,'-o',output,'-d']
        elif combine:
            command = ['python2', 'justOrthologs.py', '-q', query,'-s',subject,'-t',threads,'-o',output,'-c']
        else:
            command = ['python2', 'justOrthologs.py', '-q', query,'-s',subject,'-t',threads,'-o',output]
        prog=  subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except Exception:
        print "Error Occurred in Running JustOrthologs"
    return prog


if __name__ =='__main__':
    '''
    MAIN
    '''
    TEMP_FILE_NUM = str(int(os.urandom(3).encode('hex'),16))
    while checkTempNum(TEMP_FILE_NUM):
        TEMP_FILE_NUM = str(int(os.urandom(3).encode('hex'),16))
    args = parseArgs()
    
    proc1 = None
    proc2 = None
    extract1=None
    extract2=None
    sort1 = None
    sort2 = None
    
    ##Take 2 genomes and 2 gff3 files from start to finish
    if args.gff3_One and args.ref_One and args.extract:
        proc1,extract1 = runExtract(args.gff3_One,args.ref_One,args.keep,1)
    
    if args.gff3_Two and args.ref_Two and args.extract:
        proc2,extract2 = runExtract(args.gff3_Two,args.ref_Two,args.keep,2)
    
    if proc1 is not None:
        proc1.communicate()
        filter1 = ""
        if args.filter:
            filterProc,filter1 = runFilter(extract1,1)
            filterProc.communicate()
        if filter1 =="":
            filter1 = extract1
        if args.sort:
            temp1 = ".sort_1" +"_" + TEMP_FILE_NUM
            if proc2 is None and args.output is not None:
                temp1 = args.output
            sortProc,sort1 = runSort(filter1,temp1)
            sortProc.communicate()
            if not args.keep:
                
                os.remove(extract1)
                if  os.path.isfile(filter1):
                    os.remove(filter1)
            else:
                print "Extracted file for",args.ref_One,"is located in:",extract1
                if  filter1!=extract1:
                    print "Filtered file for",args.ref_One,"is located in:",filter1
        elif not args.keep:
            print "Filtered file for",args.ref_One,"is located in:",filter1

    if proc2 is not None:
        proc2.communicate()
        filter2 = ""
        if args.filter:
            filterProc,filter2 = runFilter(extract2,2)
            filterProc.communicate()
        if filter2 =="":
            filter2 = extract2
        if args.sort:
            temp2 = ".sort_2" +"_" + TEMP_FILE_NUM
            sortProc,sort2 = runSort(filter2,temp2)
            sortProc.communicate()
            if not args.keep:
                os.remove(extract2)
                if  os.path.isfile(filter2):
                    
                    os.remove(filter2)
            else:
                print "Extracted file for",args.ref_Two,"is located in:",extract2
                if  filter2!=extract2:
                    print "Filtered file for",args.ref_Two,"is located in:",filter2
        elif not args.keep:
            print "Filtered file for",args.ref_One,"is located in:",filter1

    

    if args.fasta1:
        filter1 =""
        if args.filter:
            filterProc,filter1 = runFilter(args.fasta1,1)
            filterProc.communicate()
        if filter1=="":
            filter1 = args.fasta1
        if args.sort:
            temp1 = ".sort_1" +"_" + TEMP_FILE_NUM
            sortProc,sort1 = runSort(filter1,temp1)
            sortProc.communicate()
            if not args.keep  and filter1!=args.fasta1:
                
                os.remove(filter1)
            else:
                if  filter1!=args.fasta1:
                    print "Filtered file for",args.fasta1,"is located in:",filter1
        else:
            sort1=args.fasta1
    
    if args.fasta2:
        filter2 = ""
        if args.filter:
            filterProc,filter2 = runFilter(args.fasta2,2)
            filterProc.communicate()
        if filter2=="":
            filter2 = args.fasta2
        if args.sort:
            temp2 = ".sort_2"+"_" + TEMP_FILE_NUM
            sortProc,sort2 = runSort(filter2,temp2)
            sortProc.communicate()
            if not args.keep and filter2!=args.fasta2:
                
                os.remove(filter2)
            else:
                if  filter2!=args.fasta2:
                    print "Filtered file for",args.fasta2,"is located in:",filter2
        else:
            sort2=args.fasta2
    if sort1 is not None and sort2 is not None:
        if  os.stat(sort1).st_size==0:
            print "Make sure input files are in the correct format"
            cleanUp(False)
            sys.exit()
        if  os.stat(sort2).st_size==0:
            print "Make sure input files are in the correct format"
            cleanUp(False)
            sys.exit()
        
        if args.run:
            threads = "16"
            if args.threads:
                threads = str(args.threads)
            distant = False
            if args.distant:
                distant = True
            combine = False
            if args.combine:
                combine = True
            
            prog=runJustOrthologs(sort1,sort2,threads,args.output,distant,combine)
            prog.communicate()
            output = open(args.output,'w')
            output.write("Ortholog Group\t" + args.ref_One + "\t" + args.ref_Two +"\n")
            firstOne = True
            for line in open(args.output + TEMP_FILE_NUM,'r'):    
                if firstOne:
                    firstOne =False
                    continue
                output.write(line)

            os.remove(args.output + TEMP_FILE_NUM)
            
            if not args.keep:
                if not args.fasta2 or args.fasta2!=sort2:
                    
                    os.remove(sort1)
                    os.remove(sort2)
        else: 
            print "Sorted files are located in:",sort1, "and", sort2

    elif sort1 is not None and args.ref_One is not None:    
        if  os.stat(sort1).st_size==0:
            print "Make sure input files are in the correct format"
            cleanUp(False)
            sys.exit()
        if args.output:
            correctOutput = args.output 
            command = [ 'mv', sort1, correctOutput]
            prog=  subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            prog.communicate()
            
            print "Sorted file is located in:",correctOutput
        else:
            print "Sorted file is located in:",sort1






