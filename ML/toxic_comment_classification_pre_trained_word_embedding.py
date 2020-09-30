# -*- coding: utf-8 -*-
"""Toxic Comment Classification Pre-Trained Word Embedding.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1qUfcpwVGL3Vg0GNG9RSzE3Zd45fVKA47

# Import the dataset
"""

import pandas as pd
import numpy as np
import spacy
from tqdm import tqdm
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import GridSearchCV, cross_val_score

import re
import gc

tqdm.pandas()

! python -m spacy download en_core_web_lg

! python -m spacy link en_core_web_lg en --force

! pip install kaggle

from google.colab import files
files.upload()

! mkdir ~/.kaggle
! cp kaggle.json ~/.kaggle/

! chmod 600 ~/.kaggle/kaggle.json

! kaggle competitions download -c jigsaw-toxic-comment-classification-challenge

! mkdir dataset

! unzip test.csv.zip -d dataset

! unzip train.csv.zip -d dataset

"""# Preprocessing"""

data = pd.read_csv('dataset/train.csv', dtype={'comment_text':'string'})
data.head()

test_data = pd.read_csv('dataset/test.csv', dtype={'comment_text':'string'})
test_data.head()

data = data.drop(columns='id')
data.head()

ids = test_data.iloc[:,0]
ids

test_data = test_data.drop(columns='id')
test_data.head()

def to_lower(text):
  return text.lower()

def remove_abbreviation(text):
    text = re.sub("^ *","", text)
    text = re.sub("\n"," ",text)
    text = re.sub(' {2,}', ' ', text)
    text = re.sub("\[.*\]"," ",text)
    text = re.sub("\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}"," ",text)
    text = re.sub(r"\?"," ",text)
    text = re.sub("don'?t","do not",text)
    text = re.sub("doesn'?t", "does not",text)
    text = re.sub("didn'?t", "did not",text)
    text = re.sub("hasn'?t", "has not",text)
    text = re.sub("haven'?t", "have not",text)
    text = re.sub("hadn'?t", "had not",text)
    text = re.sub("won'?t", "will not",text)
    text = re.sub("wouldn'?t", "would not",text)
    text = re.sub("can'?t", "can not",text)
    text = re.sub("cannot", "can not",text)
    text = re.sub("i'?m", "i am",text)
    text = re.sub("i'?ll", "i will",text)
    text = re.sub("it'?s", "it is",text)
    text = re.sub("that'?s", "that is",text)
    text = re.sub("weren'?t", "were not",text)
    text = re.sub("i'?d","i would",text)
    text = re.sub("i'?ve","i have",text)
    text = re.sub("she'?d","she would",text)
    text = re.sub("they'?ll","they will",text)
    text = re.sub("they'?re","they are",text)
    text = re.sub("we'?d","we would",text)
    text = re.sub("we'?ll","we will",text)
    text = re.sub("we'?ve","we have",text)
    text = re.sub("it'?ll","it will",text)
    text = re.sub("there'?s","there is",text)
    text = re.sub("where'?s","where is",text)
    text = re.sub("they'?re","they are",text)
    text = re.sub("let'?s","let us",text)
    text = re.sub("couldn'?t","could not",text)
    text = re.sub("shouldn'?t","should not",text)
    text = re.sub("wasn'?t","was not",text)
    text = re.sub("could'?ve","could have",text)
    text = re.sub("might'?ve","might have",text)
    text = re.sub("must'?ve","must have",text)
    text = re.sub("should'?ve","should have",text)
    text = re.sub("would'?ve","would have",text)
    text = re.sub("who'?s","who is",text)
    text = re.sub("you'?re", "you are", text)
    text = re.sub("y'?all", "you all", text)
    text = re.sub("'d've"," would have", text)
    text = re.sub("'d"," would", text)
    text = re.sub("'re"," are", text)
    text = re.sub("'ve"," have", text)
    text = re.sub("\bim\b", "i am",text)
    text = re.sub("[^a-zA-Z .,]+", "", text)
    return text

def remove_url(text):
  text = re.sub(r"\b(?:(?:https|ftp|http|www)://)?\w[\w-]*(?:\.[\w-]+)+\S*", '', text, flags=re.MULTILINE)
  return text

def preprocessing_pipeline(text):
  text = to_lower(text)
  text = remove_url(text)
  text = remove_abbreviation(text)
  return text

data['comment_text'] = data.loc[:,'comment_text'].apply(lambda text : preprocessing_pipeline(text))

test_data['comment_text'] = test_data.loc[:,'comment_text'].apply(lambda text : preprocessing_pipeline(text))

data.shape

test_data.shape

del preprocessing_pipeline
del to_lower
del remove_url
del remove_abbreviation

gc.collect()

"""# Word Embedding"""

nlp = spacy.load('en')
doc = nlp(u"Chicken and Mutton")
doc.vector

X = np.zeros((data.shape[0], 300), dtype=np.float32)
counter = 0

def word_embedding(text):
  global counter
  X[counter,:] = nlp(text).vector
  counter = counter + 1

data.loc[:,'comment_text'].progress_apply(lambda text : word_embedding(text))

X

X.shape

Test = np.zeros((test_data.shape[0], 300), dtype=np.float32)
counter = 0

def word_embedding_test(text):
  global counter
  Test[counter,:] = nlp(text).vector
  counter = counter + 1

test_data.loc[:,'comment_text'].progress_apply(lambda text : word_embedding_test(text))

Test.shape

Test

Y = data.iloc[:,1:].values
Y

categories = data.iloc[:,1:].columns
categories

del data
del test_data

gc.collect()

"""# Decision Trees"""

scores = 0

# alpha_values = [0.9999999999999999, 0.25, 0.85, 0.1, 0.7, 0.25]

for index,category in enumerate(categories):
    decision_tree = DecisionTreeClassifier(max_depth=300)
    score = np.mean(cross_val_score(decision_tree, X, Y[:,index], cv=3, scoring='roc_auc'))
    scores += score
    print(f"{category} : {score}")

print("\nAverage Score : {:.5f}".format(scores/6))