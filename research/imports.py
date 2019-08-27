# Author:  DINDIN Meryll
# Date:    27 August 2019
# Project: AsTeR

# General imports
import os
import time
import json
import tqdm
import joblib
import argparse
import numpy as np
import pandas as pd

# Training linked metrics
from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score
from sklearn.metrics import f1_score
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import cohen_kappa_score
from sklearn.model_selection import train_test_split
from multiprocessing import cpu_count, Pool

# NLP relative packages
from nltk.corpus import words
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import CountVectorizer

# Visualization packages
try: 
    import seaborn as sns
    import matplotlib.pyplot as plt
    import matplotlib.gridspec as gridspec
    from matplotlib import cm
except: pass

# Challenger package imported
from optimizers import Prototype, Bayesian, Logger