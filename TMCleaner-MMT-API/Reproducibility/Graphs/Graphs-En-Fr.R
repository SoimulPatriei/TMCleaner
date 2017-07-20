library(calibrate)

# Data for English-French
x<-c(1,2,3,4,5,6,7,8,9,10)
F_positive<-c(0.81,0.84,0.86,0.86,0.86,0.86,0.86,0.87,0.88)
F_negative<-c(0.77,0.83,0.86,0.85,0.86,0.86,0.86,0.86,0.88)

l_positive<- c("KN","DT","MV","LR","LN","RBF","AB","SK","BG")
l_negative<- c("KN","DT","","LR","","","","SK","")


#Plot the bar chart.
plot(F_positive,type = "o", xlab = "Classifier", ylab = "F1-score", main = "English-French", 
     ylim=c(0.75,0.9), xlim=c(0,11),cex.lab=1.5, cex.axis=1.5, cex.main=1.5, cex.sub=1.5)
lines(F_negative, type = "o", pch=22, lty=2)

textxy(x, F_positive, l_positive,cex=1.5)
textxy(x, F_negative,l_negative,cex=1.5)
