library(gdata)
# pacakge gdata with function read.xls to parse xls files.

inXLS <- ""
outPDF <- ""

data <- read.xls(inXLS)
data <- as.matrix(data)

pdf(file=outPDF)
for(i in 5:13){
    content <- data[(data[,i]!="" & !is.na(data[,i])),i]
    inpie <- table(content)
    pie(inpie,main=colnames(data)[i],cex=0.5)
    mtext(paste("Number of records:",length(content),sep=""), side=1, line=1)
}
dev.off()
