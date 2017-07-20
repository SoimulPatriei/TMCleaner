library(calibrate)

# Data for English-Italian
x<-c(1,2,3,4,5,6,7,8,9,10)
F_positive<-c(0.93,0.93,0.93,0.93,0.93,0.93,0.94,0.94,0.95)
F_negative<-c(0.72,0.65,0.69,0.69,0.69,0.73,0.72,0.73,0.76)

l_positive<- c("RBF","KN","DT","SK","BG","AB","MV","LR","LN")

#Plot the bar chart.
plot(F_positive,type = "o", xlab = "Classifier", ylab = "F1-score", main = "English-Italian", 
     ylim=c(0.60,1), xlim=c(0,11),cex.lab=1.5, cex.axis=1.5, cex.main=1.5, cex.sub=1.5)
lines(F_negative, type = "o", pch=22, lty=2)

textxy(x, F_positive, l_positive,cex=1.5)

#Here we order by l_positive
textxy(x, F_negative, l_positive,cex=1.5)
