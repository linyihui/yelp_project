import json
import numpy as np
import pandas as pd
import pprint
import matplotlib.pyplot as plt
from collections import OrderedDict
from nltk.corpus import stopwords
from nltk import word_tokenize
from os import listdir
from os.path import isfile, join

DATASET_DIR = 'yelp_us_top_100_cities_restaurants'

def listFiles(directory):	
	return [f for f in listdir(directory) if isfile(join(directory, f))]

def readJsonFile(filename):
	with open(filename, 'r') as f:
		return json.load(f)

def printBusiness(businesses, stop_words):
	for business in businesses:
		try:
			print business['name'], business['rating'], business['review_count'], [c[1] for c in business['categories']]
		except:
			pass
		snippet = business['snippet_text']
		try:
			print snippet
			print [i for i in word_tokenize(snippet) if i not in stop_words], '\n'
		except:
			pass

def addSnippetWordListCol(df, stop_words):
	snippet_word_lists = []
	for snippet in df['snippet_text']:
		try:
			snippet_word_lists.append([i for i in word_tokenize(snippet) if i not in stop_words])
		except:
			pass
	df['snippet_no_stopwords'] = pd.Series(snippet_word_lists)

def getSnippetWordCount(df):
	total_num_words = 0
	word_count = {}
	for word_list in df['snippet_no_stopwords']:
		for w in word_list:
			total_num_words = total_num_words + 1
			if w not in word_count:
				word_count[w] = 1
			else:
				word_count[w] = word_count[w] + 1
	for k, v in word_count.items():
		word_count[k] = float(v) / total_num_words
	return OrderedDict(sorted(word_count.items(), key=lambda t: t[1], reverse=True))

def main():
	filenames = listFiles(DATASET_DIR)
	# Read from JSON files.
	businesses = []
	for filename in filenames[:2]:
		businesses.extend(readJsonFile(join(DATASET_DIR, filename)))
	print "Number of businesses:", len(businesses)

	# Load Stopwords list.
	stop_words = stopwords.words("english")

	# Convert businesses into DataFrame
	df = pd.DataFrame(businesses)
	print df.describe()

	# Add a column "snippet_no_stopwords"
	addSnippetWordListCol(df, stop_words)

	df2 = df[(df.rating >= 4.5) & (df.review_count > 100)]
	print df2['snippet_no_stopwords']

	word_count_all = getSnippetWordCount(df)
	word_count_top = getSnippetWordCount(df2)

	word_count_ratio = OrderedDict(word_count_top)
	for w, prob in word_count_ratio.items():
		word_count_ratio[w] = prob / word_count_all[w]

	keywords = pd.DataFrame(sorted(word_count_ratio.items(), key=lambda t: t[1], reverse=True))
	print keywords[0:100]

	# # print df.head()
	# # printBusiness(businesses, stop_words)

if __name__ == "__main__":
    main()