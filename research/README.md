# Machine Learning Model

This notebook presents our strategy to train our vocabulary on disaster-specific data to ultimately improve the quality of our priority score. Given the limited labeled data sets on emergency calls, we decided to use a labeled Twitter data set that was presented by Muhammad Imran, Prasenjit Mitra, Carlos Castillo: Twitter as a Lifeline: Human-annotated Twitter Corpora for NLP of Crisis-related Messages. In Proceedings of the 10th Language Resources and Evaluation Conference (LREC), pp. 1638-1643. May 2016, Portorož, Slovenia. The dataset can be found at https://crisisnlp.qcri.org/lrec2016/lrec2016.html.

## The notebook presents the following main steps:

- Data Preprocessing and Cleaning: Load the data, merge single files into one dataframe and remove Twitter specific labels and signs.
- Train a Random Forest Classifier on the vectorized text data. We train one against all in for two different types of classes: (1) Content and (2) Category.
- The output is a list of features and their corresponding feature importance for Content and Category, respectively.

More text in plain format
