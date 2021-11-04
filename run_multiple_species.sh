#! /bin/bash

OPTIND=1         # Reset in case getopts has been used previously in the shell.
input_dir=""
output_dir=""
end_output=""
gff_extension=".gff3"
fasta_extension=".fasta"
while getopts "h?:f:g:i:e:o:" opt; do
    case "$opt" in
    h|\?)
	echo "-i is a required directory with input .fasta and .gff3 files. "
		echo "-o is a required output directory for pairwise JustOrtholog comparisons"
		echo "-e is a required end output file for the combined analysis"
		echo "-f is optional and is the extension for fasta files in the input directory. Default=.fasta"
		echo "-g is optional and is the extension for gff3 files in the input directory. Default=.gff3"
		echo "-h shows this help message"
		echo "-v shows verbose messages of progress"
        exit 0
        ;;
	i)	input_dir=$OPTARG
		if [[ "${input_dir: -1}" != '/' ]]; then
			input_dir=${input_dir}"/"	
		fi
		input_dir=${input_dir}"*"
		;;
	e)	end_output=$OPTARG
		;;
	g)	gff_extension=$OPTARG
		;;
	f)	fasta_extension=$OPTARG
		;;
    o)  output_dir=$OPTARG
		if [[ "${output_dir: -1}" != '/' ]]; then
			output_dir=${output_dir}"/"	
		fi
		mkdir -p ${output_dir}
    esac
done
shift $(( OPTIND-1 )) 

SED_EXEC="sed"
OS_TYPE=`uname -s`
if [ "${OS_TYPE}" == "Darwin" ]
then
            SED_EXEC="gsed"
fi
set -- `ls -1 ${input_dir} | ${SED_EXEC} -e 's/\..*$//' | uniq`
for a; do
	file_a=`basename ${a%%.*}`
    shift
    for b; do
		file_b=`basename ${b%%.*}`
		python2 wrapper.py -g1 "${a}${gff_extension}" -g2 "${b}${gff_extension}" -r1 "${a}${fasta_extension}" -r2 "${b}${fasta_extension}" -all -o ${output_dir}/${file_a}_${file_b}
    done
done

python2 combineOrthoGroups.py -id ${output_dir} -o ${end_output}

