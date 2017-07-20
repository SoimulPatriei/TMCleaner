This is the README file for the paper " Ensembles of classifiers for cleaning parallel corpora and translation memories in a multilingual setting" 

Here are the instructions that allow you to reproduce the results in the paper: tables and graphs.

Prerequisites:
 1.  Pyhton 2.7.12 or newer
 2.  scikit-learn 0.18 or newer
 3. mlxtend package (Install it from here => http://rasbt.github.io/mlxtend/installation/)
 4. "R environment" for R scripts and graphs generation.



I. The contents of the root directory is the following :
1. Ensemble --- In this directory is everything necessary to run the individual classifiers, the ensemble of classifiers and the evaluation script.

2. Graphs --- In this directory there are two R scripts for reproducing the graphs in the paper

3. Results ----In this directory you have the results of the classification and evaluation that you can reproduce running the scripts in the Ensemble directory 

II. Classifying and Evaluating 
		cd Ensemble

The contents of the directory Ensemble is :

Annotated ----------------------> The manually annotated test sets
Config  ---------------------->  Configuration files for the scripts
Test    -----------------------> The test sets in scikit-learn format
Training ------------------------> The training sets in scikit-learn format
evaluate.py --------------------> The evaluation script
ensemble.py --------------------> The script for running all classifiers (individual and ensemble)
LoadData.py --------------------> auxiliary script
Models.py -----------------------> auxiliary script
produceHTMLFormat.py------>auxiliary script


Open the script ensemble.py and read the instructions at the top. You will obtain the results in a directory.

     python ensemble.py --config Config/c-Italian.txt --resultsdir English-Italian-Classified
     
     python ensemble.py --config Config/c-French.txt --resultsdir English-French-Classified 

For evaluation open the evaluate.py script and read the instructions at the top.  The results will also be in a directory. For each classifier we provide two evaluation files. The file ending in *-statistics.txt contains the scores (F1-score) and balanced accuracy. The file ending in .html contains a nice view of the manual and classified set stressing the errors.

	python evaluate.py --resultsdir English-Italian-Classified --manual Annotated/English-Italian.txt --evdir English-Italian-Evaluate
	
	python evaluate.py --resultsdir English-French-Classified   --manual Annotated/English-French.txt --evdir English-French-Evaluate
	
III. Reproducing the graphs.
Inside the directory Graphs there are two R scripts :
      Graphs-En-It.R reproduces the graphs for English-Italian
      Graphs-En-Fr.R reproduces the graphs for English-French


