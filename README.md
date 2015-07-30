# Yelp Project
Many consumer-facing websites, like Yelp and Amazon, have collected tons of customer reviews. While these reviews can be useful for resource for the platform and end users, most of them are unstructured and not actionable. This is an ongoing project that aims to extract keywords from reviews, analyze their correlation with popularity, and turn review text into actionable insights.

## Overview
The major components of the project: 
- yelp-data-crawler
  - Crawls business data from Yelp using [Yelp API](https://www.yelp.com/developers/documentation/v2/overview).
  - Writes data into SQL database or JSON files.
- yelp-data-analyzer
  - Reads business data from SQL database or JSON files.
  - Parse and clean review snippet text using Natural Language Processing techniques, including tokenizations and stopwords removal.
  - Compute statistics of keywords in snippet text.
  - Train and evaluate machine-learned models to predict whether a restaurant is highly-rated given review text. Currently supports Logistic Regression and Decision Tree classifiers.
- yelp-data-visualizer
  - Visualize the statistics of keywords in snippet text and plot the correlations.
  - Explore the importance of keywords in different cities in Word Clouds.
- sql_helper
  - Helper functions to create, query, and insert data into SQL databases.