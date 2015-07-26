import numpy as np
import pandas as pd
import random
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS

def scatter(xs, ys, labels):
	fig, ax = plt.subplots()
	ax.scatter(xs, ys)
	for x, y, label in zip(xs, ys, labels):
		ax.annotate(label, (x, y))
	plt.show()

def scatter_color(xs, ys, labels, colors, areas):
	fig = plt.figure()
	plt.subplots_adjust(bottom = 0.1)
	plt.scatter(
	    xs, ys, marker='o', c=colors, s=areas,
	    cmap = plt.get_cmap('Spectral'))
	# fig.suptitle('Word Distribution')
	plt.xlabel('Word Probability in all restaurants')
	plt.ylabel('Word Probability in highly-rated Restaurants')
	for label, x, y in zip(labels, xs, ys):
	    plt.annotate(
	        label, 
	        xy = (x, y), xytext = (-20, 20),
	        textcoords = 'offset points', ha = 'right', va = 'bottom',
	        bbox = dict(boxstyle = 'round,pad=0.5', fc = 'yellow', alpha = 0.5),
	        arrowprops = dict(arrowstyle = '->', connectionstyle = 'arc3,rad=0'))

	plt.show()

def generateWordCloud(list_word_freq):
	wordcloud = WordCloud(width=1200, height=1000, background_color='white', stopwords=STOPWORDS)
	wordcloud.generate_from_frequencies(list_word_freq)
	plt.imshow(wordcloud)
	plt.axis('off')
	plt.show()

def generateScatterPlot(df):
	selected_index = random.sample(df.index, 100)
	df = df.ix[selected_index]

	xs = df.word_count_all.tolist()
	ys = df.word_count_top.tolist()
	labels = df.word.tolist()
	# scatter(xs, ys, labels)
	scatter_color(xs, ys, labels, np.random.rand(len(xs)), df.word_count_all.tolist())

def main():
	df = pd.read_csv("word_count_nyc_filtered.csv")
	print df.head()
	generateScatterPlot(df)	
	
	words = df.word.tolist()
	counts = df.word_count_all.tolist()
	generateWordCloud([(word, count) for (word, count) in zip(words, counts)])
	
if __name__ == "__main__":
    main()