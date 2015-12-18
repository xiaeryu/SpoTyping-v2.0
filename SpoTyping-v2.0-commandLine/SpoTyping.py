## Copyright (C) 2015 Xia Eryu (xiaeryu@nus.edu.sg).
##
## This program is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License
## as published by the Free Software Foundation; either version 3
## of the License, or (at your option) any later version.

## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.

## You should have received a copy of the GNU General Public License
## along with this program; if not, see 
## http://www.opensource.org/licenses/gpl-3.0.html

## SpoTyping.py
## --------------------------------
## Please report bugs to:
## xiaeryu@u.nus.edu

import sys
import os
import re
from optparse import OptionParser
import subprocess
import gzip
import urllib
import urllib2

## Global variables
dir = os.path.split(os.path.realpath(__file__))[0] # script directory
setlength = 50*5000000                             # base input cut-off for swift mode

## Option variables
usage = "usage: %prog [options] FASTQ_1/FASTA FASTQ_2(optional)"
parser = OptionParser(usage=usage, version="%prog 2.0")
parser.add_option("--seq",action="store_true",dest="seq",help="Set this if input is a fasta file that contains only a complete genomic sequence or assembled contigs from an isolate [Default is off]")
parser.add_option("-s","--swift",action="store",type="string",dest="swift",default="on",help="swift mode, either \"on\" or \"off\" [Defulat: on]")
parser.add_option("-m","--min",action="store",type="int",dest="min",default=5,help="minimum number of error-free hits to support presence of a spacer [Default: 5]")
parser.add_option("-r","--rmin",action="store",type="int",dest="min_relax",default=6,help="minimum number of 1-error-tolerant hits to support presence of a spacer [Default: 6]")
parser.add_option("-O","--outdir",action="store",type="string",dest="outdir",default=".",help="output directory [Default: running directory]")
parser.add_option("-o","--output",action="store",type="string",dest="output",default="SpoTyping",help="basename of output files generated [Default: SpoTyping]")
parser.add_option("--noQuery",action="store_true",dest="noQuery",help="Suppress the SITVIT database query [Default is off]")
parser.add_option("-d","--debug",action="store_true",dest="debug",help="enable debug mode, keeping all intermediate files for checking [Default is off]")
(options, args) = parser.parse_args()

noQuery = options.noQuery
seq = options.seq                    # input file contains a completegenomic sequence
swift = options.swift                # swift mode, default is on
min = options.min                    # minimum number of exact reads to support existence of spacer sequence
min_relax = options.min_relax        # minimum number of approximate reads, allowing for 1 mismatch to support existence of spacer sequence
outdir = options.outdir              # output directory.
output = options.output              # basename of output files
debug = options.debug                # debug mode

## Check input fastq files
narg = len(args)
if narg == 0:
    print usage
    sys.exit()
elif narg == 1:
    input1 = args[0]    # Input fastq file 1
    if not os.path.isfile(input1):
        print "ERROR: Invalid FASTQ_1/FASTA file!"
        sys.exit()
elif narg == 2:
    if seq:
        print "ERROR: Only one fasta file is allowed when '--seq' is set!"
        sys.exit()
    input1 = args[0]    # Input fastq file 1
    input2 = args[1]    # Input fastq file 2
    if not os.path.isfile(input1):
        print "ERROR: Invalid FASTQ_1 file!"
        sys.exit()
    elif not os.path.isfile(input2):
        print "ERROR: Invalid FASTQ_2 file!"
        sys.exit()

if seq:
    min = min_relax = 1


############################################################
## Main class is described here
############################################################
class Main:
    def concatenation(self,in_file,out_handle):  # Concatenate sequences without length check
        if in_file.endswith(".gz"):
            in_handle = gzip.open(in_file, 'rb')
        else:
            in_handle = open(in_file)
        count = 0
        for line in in_handle:
            line = line.strip('\n')
            if count % 4 == 1:
                out_handle.write(line)
            count = (count+1) %4
        in_handle.close()

    def concatenation_check(self,in_file,out_handle,cutoff):  # Concatenate sequences with length check
        if in_file.endswith(".gz"):
            in_handle = gzip.open(in_file, 'rb')
        else:
            in_handle = open(in_file)
        count = 0
        outlength = 0
        for line in in_handle:
            line = line.strip('\n')
            if outlength > setlength:
                break
            elif count % 4 == 1:
                out_handle.write(line)
                outlength += len(line)
            count = (count+1) %4
        in_handle.close()
        return outlength

    def parse_blast(self,in_file,log_handle,out_handle):  # Parse blast output file
        record = {}
        record_relax = {}
        for i in range(1,44):
            record["Spacer%d" % i] = 0
            record_relax["Spacer%d" % i] = 0

        spotype = ""

        file_blast = open(in_file)
        for line in file_blast:
            line = line.strip("\n")
            if not re.search('#',line):
                tmp = re.split('\s+',line)
                tmp[2] = float(tmp[2])
                tmp[3] = int(tmp[3])
                if tmp[2]==100 and tmp[3]==25:
                    record[tmp[0]]+=1
                    record_relax[tmp[0]]+=1
                elif (tmp[2]==96 and tmp[3]==25) or (tmp[2]==100 and tmp[3]==24):
                    record_relax[tmp[0]]+=1
        file_blast.close()

        storage=[]
        for i in range(1,44):
            signal =0
            if (record["Spacer%d" % i] >= min) or (record_relax["Spacer%d" % i]) >= min_relax:
                signal = 1
            storage.append(signal)
            log_handle.write("Spacer%d\t%d\t%d\t%d\n" % (i,record["Spacer%d" % i], record_relax["Spacer%d" % i],signal))

        out_handle.write("%s\t" % ''.join([str(item) for item in storage]))

        for i in range(0,40,3):
            value = 4*storage[i]+2*storage[i+1]+storage[i+2]
            out_handle.write("%d" % value)
            spotype ="%s%d" % (spotype,value)

        out_handle.write("%d" % storage[42])
        spotype = "%s%d" % (spotype,storage[42])
        out_handle.write("\n")

        return spotype


############################################################
## SITVIT database query module is described here
############################################################
class querySITVIT:
    def post(self, url, data):
        req = urllib2.Request(url)
        data = urllib.urlencode(data)
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
        response = opener.open(req, data, timeout=500)
        return response.read()

    def query(self,Qtype,out_handle):
        data = {
            "action": "validationFormulaire",
            "changeView": "false",
            "clade": "",
            "doGeoRepart": "false",
            "exportXLS": "true",
            "inves": "",
            "iso": "",
            "isoNumber": "",
            "mapType": "spo_map",
            "miru": "",
            "mit": "",
            "nStrains": "",
            "ori": "",
            "remarks": "",
            "sit": "",
            "spoligo": Qtype,
            "strainName": "",
            "vit": "",
            "vntr": "",
            "year": "",
        }
        url = "http://www.pasteur-guadeloupe.fr:8081/SITVIT_ONLINE/query"
        response = self.post(url, data)
        out_handle.write(response)



############################################################
## Code starts here
############################################################
if __name__ == "__main__":
    t = Main()

    ## Check name of existing tmp files
    tmpnum = 0
    while os.path.isfile("%s.SpoTyping.tmp.%d" % (output,tmpnum)):
        tmpnum+=1
    tmpfile = "%s/%s.SpoTyping.tmp.%d" % (outdir,output,tmpnum)

    ##########################################################
    ## Create a fasta file with the reads concatenated.
    ##########################################################
    if not seq:
        file_tmp = open(tmpfile, 'w')
        file_tmp.write(">Combine\n")

        if swift == 'on':
            out_first = t.concatenation_check(input1,file_tmp,setlength)
            remaining = setlength - out_first          
            if (narg == 2) and (remaining > 0):
                t.concatenation_check(input2,file_tmp,remaining)

        else:
            t.concatenation(input1,file_tmp)
            if narg == 2:
                t.concatenation(input2,file_tmp)
    
        file_tmp.write("\n")
        file_tmp.close()


    ##########################################################
    ## Blast the spacers against the concatenated fasta file.
    ##########################################################
    blastDB = tmpfile
    if seq:
        blastDB = input1

    tmpH = open("%s.blast.out" % tmpfile, 'w')
    subprocess.call(["makeblastdb", "-in", blastDB, "-out", blastDB, "-dbtype", "nucl"])
    subprocess.call(["blastn", "-query", "%s/ref/spacer.fasta" % dir, "-db", blastDB, "-task", "blastn", "-dust", "no", "-outfmt", "7", "-max_target_seqs", "1000000"], stdout=tmpH)
    tmpH.close()

    ##########################################################
    ## Parsing blast output & write to the output directory
    ##########################################################
    logname = outdir + '/' + output + '.log'
    log = open(logname,'a')
    out_file = open("%s/%s" % (outdir,output),'a')
    log.write("## %s\n" % input1)
    log.write("Spacer\tError-free_number\t1-error-tolerant_number\tCode\n")
    if narg == 2:
        out_file.write("%s&%s\t" % (input1,input2))
    else:
        out_file.write("%s\t" % input1)

    SpoType = t.parse_blast("%s.blast.out" % tmpfile,log,out_file)

    out_file.close()
    log.close()

    ##########################################################
    ## Query the database
    ##########################################################
    if not noQuery and not os.path.isfile("%s/SITVIT_ONLINE.%s.xls" % (outdir,SpoType)):
        query_handle = open("%s/SITVIT_ONLINE.%s.xls" % (outdir,SpoType), "wb")
        a = querySITVIT()
        a.query(SpoType,query_handle)
        query_handle.close()

    ##########################################################
    ## Cleaning up
    ##########################################################
    if not debug:
        post = ['','.blast.out','.reference']
        for i in post:
            if os.path.isfile("%s%s" % (tmpfile,i)):
                os.remove("%s%s" % (tmpfile,i))

        post2 = ['.nsq','.nhr','.nin']
        for i in post2:
            if os.path.isfile("%s%s" % (blastDB,i)):
                os.remove("%s%s" % (blastDB,i))
