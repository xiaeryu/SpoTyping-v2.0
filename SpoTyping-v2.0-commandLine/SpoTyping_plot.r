library(gdata)
# pacakge gdata with function read.xls to parse xls files.

args <- commandArgs(TRUE)

## args[1]: the input excel file
## args[2]: the output pdf file

data <- read.xls(args[1])
data <- as.matrix(data)

pdf(file=args[2])
for(i in 5:13){
    content <- data[(data[,i]!="" & !is.na(data[,i])),i]
    inpie <- table(content)
    pie(inpie,main=colnames(data)[i],cex=0.5)
    mtext(paste("Number of records:",length(content),sep=""), side=1, line=1)
}
dev.off()
