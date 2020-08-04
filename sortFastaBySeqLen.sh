#! /bin/bash

# ----------------  COLOR MANAGEMENT  ------------------------------------ ||
RED="\e[0;31m"
LRED="\e[1;31m"
GREEN="\e[0;32m"
LGREEN="\e[1;32m"
BLUE="\e[0;34m"
LBLUE="\e[1;34m"
CYAN="\e[0;36m"
LCYAN="\e[1;36m"
PURPLE="\e[0;35m"
YELLOW="\e[0;33m"
LYELLOW="\e[1;33m"
NC="\e[0m" # No color

# ----------------  MAIN SCRIPT ------------------------------------------ ||
USAGE="  USAGE: sortFasta.sh [input.fasta] [sorted_output.fasta]"
EXAMPLE="EXAMPLE: sortFasta.sh example.fasta example_sorted.fasta\n       : sortFasta.sh example.fasta > example_sorted.fasta\n       : cat example.fasta | sortFasta.sh > example_sorted.fasta"

# check if help was requested
for arg in "$@"
do
	if [ "$arg" == "-h" ] || [ "$arg" == "-help" ] || [ "$arg" == "--help" ]
	then
		printf "\n${USAGE}\n${EXAMPLE}\n\n"
		exit 0
	fi
done

# check if correct number of arguments provided
expected_args=2
if [ $# -gt $expected_args ]
then
	printf "${RED}\n  ERROR: Expected %u args, %u provided.\n\n${USAGE}\n${EXAMPLE}${NC}\n\n" ${expected_args} $#
	exit 1
fi

INPUT="${1:-/dev/stdin}"
OUTPUT="${2:-/dev/stdout}"
SED_EXEC="sed"
OS_TYPE=`uname -s`
if [ "${OS_TYPE}" == "Darwin" ]
then
            SED_EXEC="gsed"
fi

tr '\n' '\t' < ${INPUT} | ${SED_EXEC} -r 's/\t>/\n>/g' | awk -v "FS="\t" -v "OFS="\t" '{print $1,$2}' >${OUTPUT}first #| sort -n -t '	' -k 3 | ${SED_EXEC} -r 's/\t[0-9]+$//' | ${SED_EXEC} -r 's/\t/\n/' > ${OUTPUT} 
tr '\n' '\t' < ${INPUT} | ${SED_EXEC} -r 's/\t>/\n>/g' | ${SED_EXEC} 's/[^*]//g' | awk '{print length }'>${OUTPUT}second #|awk -v "FS=\t" -v "OFS=\t" '{print $1,$2}'  > ${OUTPUT}

paste ${OUTPUT}first ${OUTPUT}second | awk -v "FS="\t" -v "OFS="\t" '{print $1,$2,$3}' |sort -n -t '	' -k 3 | ${SED_EXEC} -r 's/\t/\n/' | ${SED_EXEC} -r 's/\t[0-9]+ *$//'  |${SED_EXEC} -r 's/^ +//' > ${OUTPUT} # | awk '{print $1,"\t",$2}' |${SED_EXEC} -r 's/\t/\n/' > ${OUTPUT} 

rm ${OUTPUT}first
rm ${OUTPUT}second

# exit
exit 0
