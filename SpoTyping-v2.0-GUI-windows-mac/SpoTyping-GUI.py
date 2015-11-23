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

import Tkinter
import tkFileDialog
import os
import re
import subprocess
import urllib
import urllib2
import gzip
import time

class Main(Tkinter.Tk):
    def __init__(self, parent):
        Tkinter.Tk.__init__(self,parent)
        self.parent = parent
        self.initialize()
  
    def initialize(self):
        ######################################################
        ##### Variables
        ######################################################
        self.input1 = ""	# Input file 1
        self.input2 = ""	# Input file 2
        self.blast = ""		# Dirctory to blast executables
        self.seq = False	# If True, the input is a fasta file containing complete sequence or assembled contigs
        self.swift = True	# Swift mode
        self.min = 5		# Error-free hit threshold
        self.min_relax = 6	# 1-error-tolerant hit threshold
        self.output = ""	# Output file
        self.outdir = ""	# Output directory
        self.reference = self.loadData()	# Spacer sequences as the reference
        self.setlength = 50*5000000		# The maximum number of bases taken in in the swift mode


        #####################################################
        ##### Window Layout
        #####################################################

        # Overall layout settings
        self.grid()
        self.grid_columnconfigure(0,weight=1)
        self.resizable(False, True)

        # Label of input
        Lb0 = Tkinter.Label(self, text="\n", anchor="center")
        Lb0.grid(column=1,row=0,sticky='WE')
        Lb1 = Tkinter.Label(self, text="Input", anchor="center", font = ("Helvetica", "14"))
        Lb1.grid(column=1,row=1,sticky='WE')

        # Select input type
        L0 = Tkinter.Label(self, text="Input type", anchor="w")
        L0.grid(column=0,row=2,sticky='W')

        self.type = Tkinter.BooleanVar()
        RG1 = Tkinter.Frame(self, width=80)
        RG11 = Tkinter.Radiobutton(RG1, text="Sequencing reads(fastq)", width=40, variable=self.type, value=False, command=self.selectType)
        RG11.grid(column=0,row=0,sticky="W")

        RG12 = Tkinter.Radiobutton(RG1, text="Genomic sequence(fasta)", width=40, variable=self.type, value=True, command=self.selectType)
        RG12.grid(column=1,row=0,sticky="W")
        RG11.select()
        RG1.grid(column=1,row=2,sticky='WE')
 
        # Input fastq 1
        self.var1 = Tkinter.StringVar()
        L1 = Tkinter.Label(self, text="Input Fastq 1/Fasta", anchor="w")
        L1.grid(column=0,row=3,sticky='W')

        B1 = Tkinter.Button(self, text="Browse",command=self.loadFile1)
        B1.grid(column=2,row=3,sticky="E")

        self.E1 = Tkinter.Entry(self, width=80, textvariable=self.var1)
        self.E1.grid(column=1,row=3,sticky="WE")

        B1C = Tkinter.Button(self, text="Cancel",command=self.cancel1)
        B1C.grid(column=3,row=3,sticky="E")

        # Input fastq 2
        self.var2 = Tkinter.StringVar()
        L2 = Tkinter.Label(self, text="Input Fastq 2 (Optional)", anchor="w")
        L2.grid(column=0,row=4,sticky='W')

        B2 = Tkinter.Button(self, text="Browse",command=self.loadFile2)
        B2.grid(column=2,row=4,sticky="E")

        self.E2 = Tkinter.Entry(self, width=80, textvariable=self.var2)
        self.E2.grid(column=1,row=4,sticky="WE")

        B2C = Tkinter.Button(self, text="Cancel",command=self.cancel2)
        B2C.grid(column=3,row=4,sticky="E")

        # Input blast directory
        self.var3 = Tkinter.StringVar()
        L3 = Tkinter.Label(self, text="Blast executables directory", anchor="w")
        L3.grid(column=0,row=5,sticky='W')

        B3 = Tkinter.Button(self, text="Browse",command=self.loadDir)
        B3.grid(column=2,row=5,sticky="E")

        self.E3 = Tkinter.Entry(self, width=80, textvariable=self.var3)
        self.E3.grid(column=1,row=5,sticky="WE")

        B3C = Tkinter.Button(self, text="Cancel",command=self.cancel3)
        B3C.grid(column=3,row=5,sticky="E")

        # Input output file
        self.var4 = Tkinter.StringVar()
        L4 = Tkinter.Label(self, text="Output file", anchor="w")
        L4.grid(column=0,row=6,sticky='W')

        B4 = Tkinter.Button(self, text="Browse",command=self.loadFile3)
        B4.grid(column=2,row=6,sticky="E")

        self.E4 = Tkinter.Entry(self, width=80, textvariable=self.var4)
        self.E4.grid(column=1,row=6,sticky="WE")

        B4C = Tkinter.Button(self, text="Cancel",command=self.cancel4)
        B4C.grid(column=3,row=6,sticky="E")

        # Label of parameter
        Lb2 = Tkinter.Label(self, text="", anchor="center")
        Lb2.grid(column=0,row=7,columnspan=3,sticky='WE')
        Lb3 = Tkinter.Label(self, text="Parameters", anchor="center", font = ("Helvetica", "14"))
        Lb3.grid(column=1,row=8,sticky='WE')

        # Swift mode
        L5 = Tkinter.Label(self, text="Swift mode", anchor="w")
        L5.grid(column=0,row=9,sticky='W')

        self.var5 = Tkinter.BooleanVar()
        RG2 = Tkinter.Frame(self, width=80)
        RG21 = Tkinter.Radiobutton(RG2, text="Yes", width=40, variable=self.var5, value=True, command=self.selection) 
        RG21.grid(column=0,row=0,sticky="W")

        RG22 = Tkinter.Radiobutton(RG2, text="No", width=40, variable=self.var5, value=False, command=self.selection)
        RG22.grid(column=1,row=0,sticky="W")
        RG21.select()
        RG2.grid(column=1,row=9,sticky='WE')

        # Threshold selection
        L6 = Tkinter.Label(self, text="Error-free hit threshold", anchor="w")
        L6.grid(column=0,row=10,sticky='W')

        self.entry6 = Tkinter.Entry(self, width=80)
        self.entry6.grid(column=1,row=10,sticky="WE")
        self.entry6.insert(0,5)
    
        L7 = Tkinter.Label(self, text="1-error tolerant hit threshold", anchor="w")
        L7.grid(column=0,row=11,sticky='W')

        self.entry7 = Tkinter.Entry(self, width=80)
        self.entry7.grid(column=1,row=11,sticky="WE")
        self.entry7.insert(0,6)

        # Add blank line
        L8 = Tkinter.Label(self, text="", anchor="center")
        L8.grid(column=0,row=12,columnspan=3,sticky='WE')
        L9 = Tkinter.Label(self, text="", anchor="center")
        L9.grid(column=0,row=13,columnspan=3,sticky='WE')

        # Submit, Reset, or Quit: Button settings
        BG1 = Tkinter.Frame(self)
        B1 = Tkinter.Button(BG1, width=25, text="Submit", command=self.SpoTyping)
#        B1 = Tkinter.Button(BG1, width=25, text="Submit", command=self.fakeRun)
        B2 = Tkinter.Button(BG1, width=25, text="Reset", command=self.clear)
        B3 = Tkinter.Button(BG1, width=25, text="Quit", command=self.quit)
        B1.grid(column=0,row=0,sticky="W")
        B2.grid(column=1,row=0,sticky="W")
        B3.grid(column=2,row=0,sticky="W")
        BG1.grid(column=1,row=14,sticky='WE')

        # Running process
        L10 = Tkinter.Label(self, text="", anchor="center")
        L10.grid(column=0,row=15,columnspan=3,sticky='WE')

        TG1 = Tkinter.Frame(self, width=120)
        self.scrollbar = Tkinter.Scrollbar(TG1)
        self.scrollbar.grid(column=3,row=0,sticky='WE')
        self.text = Tkinter.Text(TG1, width=118,height=45, yscrollcommand = self.scrollbar.set)
        self.text.grid(column=0,row=0,columnspan=3,sticky='E')
        TG1.grid(column=0,row=16,columnspan=4,sticky='WE')



    ##########################################################
    ##### SpoTyping
    #########################################################
    def fakeRun(self):
        for i in range(1,100):
            self.text.insert(Tkinter.INSERT,"Test running %d...\n" %i)
        self.text.insert(Tkinter.INSERT,"Test running...\n")

    def SpoTyping(self):
        self.text.configure(state="normal")
        startTime = time.clock()
        ## Get initial values and check
        self.seq = self.type.get()
        self.input1 = self.var1.get()
        self.input2 = self.var2.get()
        self.blast = self.var3.get()
        self.output = self.var4.get()
        self.swift = self.var5.get()
        self.min = self.entry6.get()
        self.min_relax = self.entry7.get()

        if self.seq:
            self.min = self.min_relax = 1

        initial = self.preCheck()
        if not initial:
            return

        ## Create query and database fasta files
        tmpnum = self.checkTmp(self.output)
        tmpfile = "%s.SpoTyping.tmp.%d" % (self.output, tmpnum)

        self.dict2fasta(self.reference, "%s.reference" % tmpfile)
        blastDB = self.input1
        if not self.seq:
            self.createFasta(tmpfile, self.swift, self.input1, self.input2, self.setlength)
            blastDB = tmpfile

        # Blast
        self.text.insert(Tkinter.INSERT,"Building blast database...\n")
        proc = subprocess.Popen(["%s/makeblastdb" % self.blast, "-in", blastDB, "-out", blastDB, "-dbtype", "nucl"], stdout=subprocess.PIPE)
        proc_info = proc.stdout.read()
        self.text.insert(Tkinter.INSERT,"%s\n" % proc_info)
		
        self.text.insert(Tkinter.INSERT,"Running blast...\n")
        tmpH = open("%s.blast.out" % tmpfile, 'w')
        subprocess.call(["%s/blastn" % self.blast, "-query", "%s.reference" % tmpfile, "-db", blastDB, "-task", "blastn", "-dust", "no", "-outfmt", "7", "-max_target_seqs", "1000000"], stdout=tmpH)
        tmpH.close()

        # Parse blast output
        self.text.insert(Tkinter.INSERT,"Parsing blast output...\n")

        logname = self.output + '.log'
        log = open(logname,'a')
        out_file = open(self.output,'a')
        log.write("## %s\n" % self.input1)
        log.write("Spacer\tError-free_number\t1-error-tolerant_number\tCode\n")
        if len(self.input2) > 2:
            out_file.write("%s&%s\t" % (self.input1,self.input2))
        else:
            out_file.write("%s\t" % self.input1)

        [binCode, SpoType] = self.parse_blast("%s.blast.out" % tmpfile,log,out_file)

        out_file.close()
        log.close()

        self.text.insert(Tkinter.INSERT,"\n\nThe predicted binary string is %s\n" % binCode)
        self.text.insert(Tkinter.INSERT,"The predicted spoligotype is %s\n" % SpoType)
        self.text.insert(Tkinter.INSERT,"Output has been saved to %s\n" % self.output)
        self.text.insert(Tkinter.INSERT,"Logfile has been saved to %s\n\n\n" % logname)

        # Query the database
        if not os.path.isfile("%s/SITVIT_ONLINE.%s.xls" % (self.outdir,SpoType)):
            self.text.insert(Tkinter.INSERT,"Searching the SITVIT database...\n")
            query_handle = open("%s/SITVIT_ONLINE.%s.xls" % (self.outdir,SpoType), "wb")
            self.query(SpoType,query_handle)
            query_handle.close()
            self.text.insert(Tkinter.INSERT,"The database query result has been saved to %s/SITVIT_ONLINE.%s.xls\n\n\n" % (self.outdir,SpoType))
        else:
            self.text.insert(Tkinter.INSERT,"%s/SITVIT_ONLINE.%s.xls already exists, will not query again...\n\n\n" % (self.outdir,SpoType))

        # Clean up
        self.text.insert(Tkinter.INSERT,"Cleaning up...\n")
        post = ['','.blast.out','.reference']
        for i in post:
            if os.path.isfile("%s%s" % (tmpfile,i)):
                os.remove("%s%s" % (tmpfile,i))

        post2 = ['.nsq','.nhr','.nin']
        for i in post2:
            if os.path.isfile("%s%s" % (blastDB,i)):
                os.remove("%s%s" % (blastDB,i))

        self.text.insert(Tkinter.INSERT,"Done! Finished in %f seconds\n" % (time.clock()-startTime))
        
        # Disable text box edit
        self.text.configure(state="disabled")


    ##########################################################
    ##### Functions for SpoTyping
    #########################################################

    ## Check before running
    def preCheck(self):
        ## Input type check and print
        if self.seq and len(self.input1)>0 and len(self.input2)>0:
            self.text.insert(Tkinter.INSERT,"ERROR: Only one input is allowed for genomic sequence (fasta)! Quit...\n")
            return False
        else:
            if not self.seq:
                self.text.insert(Tkinter.INSERT,"Input files are sequencing reads (fastq)\n")
            else:
                self.text.insert(Tkinter.INSERT,"Input file contains genomic sequences (fasta)\n")

        ## Input file check and print
        if len(self.input1) == 0:
            self.text.insert(Tkinter.INSERT,"ERROR: Input Fastq 1 or FASTA is required! Quit...\n")
            return False
        else:
            self.text.insert(Tkinter.INSERT,"Input Fastq 1/Fasta: %s\n" % self.input1)
  
        if len(self.input2) == 0:
            self.text.insert(Tkinter.INSERT,"Input Fastq 2: not applicable\n")
        else:  
            self.text.insert(Tkinter.INSERT,"Input Fastq 2: %s\n" % self.input2)

        ## Input blast directory check
        if len(self.blast) == 0:
            self.text.insert(Tkinter.INSERT,"ERROR: Blast executables directory is required! Quit...\n")
            return False
        else:
            self.text.insert(Tkinter.INSERT,"Blast executables directory: %s\n" % self.blast)

        ## Input output file check and print
        if len(self.output) == 0:
            self.text.insert(Tkinter.INSERT,"ERROR: Output file is required! Quit...\n")
            return False
        else:
            self.text.insert(Tkinter.INSERT,"Output file: %s\n" % self.output)
        
        ## Input parameters print
        self.text.insert(Tkinter.INSERT,"Swift mode: %s\n" % str(self.swift))

        self.min = int(float(self.min))
        self.min_relax = int(float(self.min_relax))
        if self.min < 0:
            self.min = 0
        if self.min_relax < 0:
            self.min_relax = 0
        self.text.insert(Tkinter.INSERT,"Error-free hit threshold: %d\n" % self.min)
        self.text.insert(Tkinter.INSERT,"1-error tolerant hit threshold: %d\n" % self.min_relax)

        return True

    ## Check the available tmp file names
    def checkTmp(self, out):
       tmp = 0
       while os.path.isfile("%s.SpoTyping.tmp.%d" % (out,tmp)):
           tmp += 1
       return tmp

    ## Convert the references stored in the dictionary to fasta
    def dict2fasta(self, inDict, outFasta):
        outH = open(outFasta, 'w')
        for item in inDict:
            outH.write('>%s\n%s\n' % (item, inDict[item]))
        outH.close()

    ## Create the fasta file from fastq
    def createFasta(self, outFile, swift, input1, input2, setlength):
        file_tmp = open(outFile, 'w')
        file_tmp.write(">Combine\n")

        if swift:
            out_first = self.concatenation_check(input1,file_tmp,setlength)
            remaining = setlength - out_first
            if len(input2)>0 and (remaining > 0):
                self.concatenation_check(input2,file_tmp,remaining)
        else:
            self.concatenation(input1,file_tmp)

        if len(input2)>0:
            self.concatenation(input2,file_tmp)

        file_tmp.write("\n")
        file_tmp.close()

    ## Concatenate without length check
    def concatenation(self,in_file,out_handle):
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

    ## Concatenate with length check
    def concatenation_check(self,in_file,out_handle,cutoff):
        if in_file.endswith(".gz"):
            in_handle = gzip.open(in_file, 'rb')
        else:
            in_handle = open(in_file)
        count = 0
        outlength = 0
        for line in in_handle:
            line = line.strip('\n')
            if outlength > self.setlength:
                break
            elif count % 4 == 1:
                out_handle.write(line)
                outlength += len(line)
            count = (count+1) %4
        in_handle.close()
        return outlength

    ## Parse blast output file
    def parse_blast(self,in_file,log_handle,out_handle):
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
            if (record["Spacer%d" % i] >= self.min) or (record_relax["Spacer%d" % i]) >= self.min_relax:
                signal = 1
            storage.append(signal)
            log_handle.write("Spacer%d\t%d\t%d\t%d\n" % (i,record["Spacer%d" % i], record_relax["Spacer%d" % i],signal))

        binCode = ''.join([str(item) for item in storage])
        out_handle.write("%s\t" % binCode)
			
        for i in range(0,40,3):
            value = 4*storage[i]+2*storage[i+1]+storage[i+2]
            out_handle.write("%d" % value)
            spotype ="%s%d" % (spotype,value)

        out_handle.write("%d" % storage[42])
        spotype = "%s%d" % (spotype,storage[42])
        out_handle.write("\n")

        return [binCode, spotype]

    ## Web query module
    def post(self, url, data):
        req = urllib2.Request(url)
        data = urllib.urlencode(data)
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
        response = opener.open(req, data, timeout=500)
        return response.read()

    ## Web query module
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

    ## Load the reference data
    def loadData(self):
        reference = {
        "Spacer1":"ATAGAGGGTCGCCGGCTCTGGATCA",
        "Spacer2":"CCTCATGCTTGGGCGACAGCTTTTG",
        "Spacer3":"CCGTGCTTCCAGTGATCGCCTTCTA",
        "Spacer4":"ACGTCATACGCCGACCAATCATCAG",
        "Spacer5":"TTTTCTGACCACTTGTGCGGGATTA",
        "Spacer6":"CGTCGTCATTTCCGGCTTCAATTTC",
        "Spacer7":"GAGGAGAGCGAGTACTCGGGGCTGC",
        "Spacer8":"CGTGAAACCGCCCCCAGCCTCGCCG",
        "Spacer9":"ACTCGGAATCCCATGTGCTGACAGC",
        "Spacer10":"TCGACACCCGCTCTAGTTGACTTCC",
        "Spacer11":"GTGAGCAACGGCGGCGGCAACCTGG",
        "Spacer12":"ATATCTGCTGCCCGCCCGGGGAGAT",
        "Spacer13":"GACCATCATTGCCATTCCCTCTCCC",
        "Spacer14":"GGTGTGATGCGGATGGTCGGCTCGG",
        "Spacer15":"CTTGAATAACGCGCAGTGAATTTCG",
        "Spacer16":"CGAGTTCCCGTCAGCGTCGTAAATC",
        "Spacer17":"GCGCCGGCCCGCGCGGATGACTCCG",
        "Spacer18":"CATGGACCCGGGCGAGCTGCAGATG",
        "Spacer19":"TAACTGGCTTGGCGCTGATCCTGGT",
        "Spacer20":"TTGACCTCGCCAGGAGAGAAGATCA",
        "Spacer21":"TCGATGTCGATGTCCCAATCGTCGA",
        "Spacer22":"ACCGCAGACGGCACGATTGAGACAA",
        "Spacer23":"AGCATCGCTGATGCGGTCCAGCTCG",
        "Spacer24":"CCGCCTGCTGGGTGAGACGTGCTCG",
        "Spacer25":"GATCAGCGACCACCGCACCCTGTCA",
        "Spacer26":"CTTCAGCACCACCATCATCCGGCGC",
        "Spacer27":"GGATTCGTGATCTCTTCCCGCGGAT",
        "Spacer28":"TGCCCCGGCGTTTAGCGATCACAAC",
        "Spacer29":"AAATACAGGCTCCACGACACGACCA",
        "Spacer30":"GGTTGCCCCGCGCCCTTTTCCAGCC",
        "Spacer31":"TCAGACAGGTTCGCGTCGATCAAGT",
        "Spacer32":"GACCAAATAGGTATCGGCGTGTTCA",
        "Spacer33":"GACATGACGGCGGTGCCGCACTTGA",
        "Spacer34":"AAGTCACCTCGCCCACACCGTCGAA",
        "Spacer35":"TCCGTACGCTCGAAACGCTTCCAAC",
        "Spacer36":"CGAAATCCAGCACCACATCCGCAGC",
        "Spacer37":"CGCGAACTCGTCCACAGTCCCCCTT",
        "Spacer38":"CGTGGATGGCGGATGCGTTGTGCGC",
        "Spacer39":"GACGATGGCCAGTAAATCGGCGTGG",
        "Spacer40":"CGCCATCTGTGCCTCATACAGGTCC",
        "Spacer41":"GGAGCTTTCCGGCTTCTATCAGGTA",
        "Spacer42":"ATGGTGGGACATGGACGAGCGCGAC",
        "Spacer43":"CGCAGAATCGCACCGGGTGCGGGAG",
        }
        return reference



    ##########################################################
    ##### Functions for window configuration
    #########################################################
    def selectType(self):
        self.seq = self.type.get()

    def cancel1(self):
        self.E1.delete(0,Tkinter.END)
        self.var1.set("")
        self.input1 = ""

    def cancel2(self):
        self.E2.delete(0,Tkinter.END)
        self.var2.set("")
        self.input2 = ""

    def cancel3(self):
        self.E3.delete(0,Tkinter.END)
        self.var3.set("")
        self.blast = ""

    def cancel4(self):
        self.E4.delete(0,Tkinter.END)
        self.var4.set("")
        self.output = ""

    def loadFile1(self):
        filename = tkFileDialog.askopenfilename()
        self.var1.set(filename)
        self.input1 = filename

    def loadFile2(self):
        filename = tkFileDialog.askopenfilename()
        self.var2.set(filename)
        self.input2 = filename

    def loadDir(self):
        dirname = tkFileDialog.askdirectory()
        self.var3.set(dirname)
        self.blast = dirname

    def loadFile3(self):
        filename = tkFileDialog.asksaveasfilename()
        self.var4.set(filename)
        self.output = filename
        self.outdir = os.path.dirname(self.output)

    def selection(self):
        self.swift = self.var5.get()

    def clear(self):
        self.type.set(False)
        self.seq = False

        self.var1.set("")
        self.input1 = ""

        self.var2.set("")
        self.input2 = ""
		
        self.var3.set("")
        self.blast = ""

        self.var4.set("")
        self.output = ""

        self.var5.set(True)
        self.swift = True
		
        self.entry6.delete(0, Tkinter.END)
        self.entry6.insert(0, 5)
        self.min = 5

        self.entry7.delete(0, Tkinter.END)
        self.entry7.insert(0, 6)
        self.min_relax = 6

        self.text.configure(state="normal")
        self.text.delete(1.0, Tkinter.END)
        self.text.configure(state="disabled")

    def quit(self):
        self.destroy()

##########################################################
##### Main function starts here
#########################################################
if __name__ == '__main__':
    app = Main(None)
    app.title("SpoTyping")
    app.mainloop()
