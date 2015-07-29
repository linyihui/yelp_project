import json
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pprint
import pydot
import random
import sql_helper
import MySQLdb
from collections import OrderedDict
from nltk.corpus import stopwords
from nltk import word_tokenize
from os import listdir
from os.path import isfile, join
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn import datasets
from sklearn import metrics
from sklearn.linear_model import LogisticRegression
from sklearn import tree
from sklearn.tree import DecisionTreeClassifier
from sklearn.externals.six import StringIO  

INPUT_SQL_TABLE = 'yelp_db_us_top_100'
DATASET_DIR = 'yelp_us_top_100_cities_restaurants'
OUTPUT_KEYWORDS_FILE = 'word_count.csv'

def listFiles(directory):	
	return [f for f in listdir(directory) if (isfile(join(directory, f)) and f.endswith('.json'))]

def readJsonFile(filename):
	with open(filename, 'r') as f:
		return json.load(f)

def readDataFrameFromSql(limit=None):
	conn = sql_helper.initSqlConnection('localhost', 'yihui', '', 'db');
	df = sql_helper.sqlTableToDataFrame(conn, INPUT_SQL_TABLE, limit)
	return df

def readDataFrameFromJson():
	filenames = listFiles(DATASET_DIR)
	print filenames
	# Read from JSON files.
	businesses = []
	for filename in filenames[:5]:
		businesses.extend(readJsonFile(join(DATASET_DIR, filename)))
	print "Number of businesses:", len(businesses)
	# Convert businesses into DataFrame.
	df = pd.DataFrame(businesses)
	return df

def printBusiness(businesses, stop_words):
	for business in businesses:
		try:
			print business['name'], business['rating'], business['review_count'], [c[1] for c in business['categories']]
		except Exception as e:
			# print "Exception: ", str(e)
			pass
		snippet = business['snippet_text']
		try:
			print snippet
			print [i for i in word_tokenize(snippet) if i not in stop_words], '\n'
		except Exception as e:
			# print "Exception: ", str(e)
			pass

def addSnippetWordListCol(df, stop_words):
	snippet_word_lists = []
	for snippet in df['snippet_text']:
		try:
			snippet_word_lists.append([i for i in word_tokenize(snippet) if i not in stop_words])
		except Exception as e:
			# print "Exception: ", str(e)
			pass
	df['snippet_no_stopwords'] = pd.Series(snippet_word_lists)

def addRestaurantRatingLabelCol(df, rating, review_counts):
	df['label'] = ((df['rating'] >= rating) & (df['review_count'] > review_counts)).astype(int)


def trainAndEval(model, X_train, y_train, X_test, y_test):
	model.fit(X_train, y_train)
	expected = y_test
	predicted = model.predict(X_test)
	# Summarize the fit of the model.
	print(metrics.classification_report(expected, predicted))
	print(metrics.confusion_matrix(expected, predicted))
	return model


def getSnippetWordCount(df):
	total_num_words = 0
	word_count = {}
	for word_list in df['snippet_no_stopwords']:
		if not isinstance(word_list, list):
			# print "[Warning] word_list:", word_list, " is not a list."
			continue
		for w in word_list:
			total_num_words = total_num_words + 1
			if w not in word_count:
				word_count[w] = 1
			else:
				word_count[w] = word_count[w] + 1
	return word_count

def createTrainingTestSets(df, training_set_ratio):
	train_rows = random.sample(df.index, int(len(df.index) * training_set_ratio))
	df_train = df.ix[train_rows]
	df_test = df.drop(train_rows)
	return df_train, df_test

def main():
	df = readDataFrameFromSql(10000)
	# df = readDataFrameFromJson()

	df = df[pd.notnull(df['snippet_text'])]

	# Load Stopwords list from nltk package.
	stop_words = stopwords.words("english")
	# Add a column "snippet_no_stopwords".
	addSnippetWordListCol(df, stop_words)

	# Compute word count of review snippets for analysis and visualization.
	df2 = df[(df['rating'] >= 4.5) & (df['review_count'] > 100)]

	word_count_all = getSnippetWordCount(df)
	word_count_top = getSnippetWordCount(df2)

	word_count_table = []	
	for w, count in word_count_top.items():
		word_count_table.append({'word': w, 'word_count_top':count, 'word_count_all':word_count_all[w]})
	word_count_df = pd.DataFrame(word_count_table)
	word_count_df.to_csv(OUTPUT_KEYWORDS_FILE, encoding='utf-8')


	# ========================================================
	# Predicting highly-rated restaurant using snippet words
	# ========================================================

	# Add a column "label"
	addRestaurantRatingLabelCol(df=df, rating=4, review_counts=50)
	
	# Split df into training set and test set.
	df_train, df_test = createTrainingTestSets(df, 0.7)

	# Create text features from training set.
	vectorizer = TfidfVectorizer(min_df=0.01, stop_words='english')	
	X_train = vectorizer.fit_transform(df_train['snippet_text'])
	print 'Vocabulary of bag-of-word vector:', vectorizer.get_feature_names()
	X_test =  vectorizer.transform(df_test['snippet_text'])
	y_train = df_train['label']
	y_test = df_test['label']

	
	# Train a L2-regularized LogisticRegression model and evaluate on test data.
	trainAndEval(model=LogisticRegression(penalty='l2', C=1.0), X_train=X_train, y_train=y_train, X_test=X_test, y_test=y_test)
	
	# Train a Decision Tree classifier and evaluate on test data.
	model = trainAndEval(model=DecisionTreeClassifier(max_depth=10), X_train=X_train, y_train=y_train, X_test=X_test, y_test=y_test)
	# Plot decisiton tree into PDF file.
	dot_data = StringIO()
	tree.export_graphviz(model, out_file=dot_data)
	graph = pydot.graph_from_dot_data(dot_data.getvalue())
	graph.write_pdf("snippet_decision_tree.pdf")


if __name__ == "__main__":
	main()