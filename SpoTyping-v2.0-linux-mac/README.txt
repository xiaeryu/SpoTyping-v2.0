SpoTyping is a software for predicting spoligotype from sequencing reads.

Part I. Spoligotype prediction and SITVIT database query.
>>> Prerequisites:
1. python
2. BLAST

>>> Input:
Fastq file or pair-end fastq files.

>>> Output:
In the output file specified:	predicted spoligotype in the format of octal code.
In the output log file:		count of hits from BLAST result for each spacer sequence. 
In the xls excel file:		spoligotype query result downloaded from SITVIT WEB.
			## Note: if the same spoligotype is queried before and have an xls file in the output directory, it will not be queried again.

>>> Usage:
python SpoTyping.py [options] FASTQ_1 FASTQ_2(optional)

An Example call:
python2.7 SpoTyping.py read_1.fastq read_2.fastq –output spo.out

>>> Options:
  --version             show program's version number and exit
  -h, --help            show this help message and exit
  -s SWIFT, --swift=SWIFT
                        swift mode, either "on" or "off" [Default: on]
  -m MIN, --min=MIN     minimum number of error-free hits to support presence of a spacer [Default: 5]
  -r MIN_RELAX, --rmin=MIN_RELAX
                        minimum number of 1-error-tolerant hits to support presence of a spacer [Default: 6]
  -O OUTDIR, --outdir=OUTDIR
                        output directory [Default: running directory]
  -o OUTPUT, --output=OUTPUT
                        basename of output files generated [Default: SpoTyping]
  -d, --debug           enable debug mode, keeping all intermediate files for checking [Default is off]

FASTQ_1        input FASTQ read 1 file (mandatory)
FASTQ_2        input FASTQ read 2 file (optional for pair-end reads)

>>> Suggestions:
1. It's highly suggested to use the swift mode (set as the default) if the sequencing throughput is no less than 100Mbp.
2. For sequencing experiments with throughputs below 100Mbp, please use -m 2 -r 3 as the thresholds.
3. If you do wish to take in all reads, it's suggested to estimated the coverage first. The --min is suggested to be set to 1/10 of the estimation to increase accuracy and to eliminate false positive. At the same time, --rmin should also be adjusted to be a bit larger than min.


Part II. Summary pie chart plot from the downloaded xls files.
>>> Prerequisites:
1. R
2. R package: gdata

>>> Input:
The xls file downloaded from SITVIT WEB.

>>> Output:
A pdf file with the information in the xls file summarized with pie charts.

>>> Usage:
Rscript SpoTyping_plot.r query_from_SITVIT.xls output.pdf

An example call:
Rscript SpoTypint_plot.r SITVIT_ONLINE.777777477760771.xls SITVIT_ONLINE.777777477760771.pdf
