import json
import re
import numpy as np
import random
import csv
import pickle
from nltk.stem.porter import *
from nltk.tokenize import RegexpTokenizer
from sklearn.cross_validation import cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import precision_score
from sklearn.preprocessing import LabelBinarizer


def fetchTrainTestStop():
	cleanedTweets = []
	sentiment = []
	stopWords = []
	testTweets = []
	testSentiment = []

	#Fetch tweets from stopwords data csv file
	with open("stopwords.txt","r") as stopWords_fh:
		stopWords = [line.rstrip() for line in stopWords_fh.readlines()]


	#Fetch tweets from train data csv file
	with open("train.csv","r",encoding='utf-8',errors='ignore') as csvfile:
		trainreader = csv.reader(csvfile)
		count =0
		for row in trainreader:
			temp_tweet = cleanTweets(row[5],stopWords)
			sentiment.append(row[0])
			cleanedTweets.append(temp_tweet)
			count = count+1

	#Fetch tweets from test data csv file
	with open("BeforeClassify.csv","r",encoding='utf-8',errors='ignore') as csvfile:
		testreader = csv.reader(csvfile)
		for row in testreader:
			testTweets.append(cleanTweets(row[3],stopWords))

	return (cleanedTweets,sentiment,testTweets)

def cleanTweets(tweet,stopWords):
	#normalize everything to lower case
	tweet = tweet.lower()

	#remove http links and replace it with a the term "URL"
	tweet = re.sub(r'(https|http)?:\/\/(\w|\.|\/|\?|\=|\&|\%)*\b', '',tweet, flags=re.MULTILINE)

	#Convert all twitter handles to the term AT_USER
	tweet = re.sub(r'(@([A-Za-z0-9_]+))','',tweet,flags = re.MULTILINE)

	words_in_tweets = tweet.split()
	
	#Remove stop words
	for each_word in words_in_tweets:
		if (each_word in  stopWords):
			words_in_tweets.remove(each_word)

	#Remove words that do not start with a letter
	for each_word in words_in_tweets:
		if(each_word[0].isdigit()==True):
			words_in_tweets.remove(each_word)
	
	tweet = ' '.join(words_in_tweets)

	return tweet


def loadData():
	with open('tweets.pkl', 'rb') as f:
	    while True:
	        try:
	            data = pickle.load(f)
	        except EOFError:
	            break
	return data


def writeToCSV(listOfTweets, listOfIds, listOfScreenNames, listOfNames):
	with open('BeforeClassify.csv', 'w') as f:
	    while True:
	        try:
	            spamwriter = csv.writer(f)
	            spamwriter.writerow(['id', 'Names', 'ScreenNames', 'Tweets', 'Labels'])
	            i = 0
	            while i < len(listOfTweets):
	            	spamwriter.writerow([listOfIds[i], listOfNames[i] ,listOfScreenNames[i], listOfTweets[i]])
	            	i = i+1
	            break
	        except EOFError:
	            break


def writeToCSVJustTweets(listOfTweets):
	with open('Tweets.csv', 'w') as f:
	    while True:
	        try:
	            spamwriter = csv.writer(f)
	            spamwriter.writerow(['Tweets'])
	            i = 0
	            while i < len(listOfTweets):
	            	spamwriter.writerow([listOfTweets[i]])
	            	i = i+1
	            break
	        except EOFError:
	            break


def readCSV():
	with open('BeforeClassify.csv', 'r') as f:
	    while True:
	        try:
	            spamreader = csv.reader(f)
	            return spamreader
	            break
	        except EOFError:
	            break


def parseTweet(tweets):
       listOfNames = []
       listOfScreenNames = []
       listOfIds = []
       listOfTweets = []
       for tweet in tweets:
       	# print("Before cleaning tweet : "+tweet['text'])
       	# clean_tweet = re.sub(r"(?:\@|https?\://)\S+", "", tweet['text'])
       	# print("After cleaning tweet : "+clean_tweet)
       	# clean_tweet = clean_tweets(tweet['text'],stopWords)
       	if tweet and 'RT' not in tweet['text'].split():
       		# print("Tweets cleaned and without retweets :"+clean_tweet)
       		listOfNames.append(tweet['user']['name'])
       		listOfIds.append(tweet['id'])
       		listOfScreenNames.append(tweet['user']['screen_name'])
       		listOfTweets.append(tweet['text'])
       		# Initially assign all the tweets as positive.
       		# listOfLabels.append(1)
       return listOfTweets, listOfIds, listOfScreenNames, listOfNames



def predictTweets(cleanedTweets,sentiment,testTweets):
	lrClassifier = LogisticRegression()
	
	vectorizer = CountVectorizer(min_df=1,ngram_range=(1,2),tokenizer = None,preprocessor = None,stop_words = None, max_features = 600)

	trainVectorizer = vectorizer.fit_transform(cleanedTweets)
	testvectorizer = vectorizer.fit_transform(testTweets)

	lrClassifier.fit(trainVectorizer,sentiment)
	res = lrClassifier.predict(testvectorizer)
	
	count = 0
	for num in res:
		print(testTweets[count],":",num)
		print()
		count = count+1

	return testTweets,res


def write(listOfTweets, listOfIds, listOfScreenNames, listOfNames, testTweets, res):
	with open('AfterClassify.csv', 'w') as f:
	    while True:
	        try:
	            spamwriter = csv.writer(f)
	            spamwriter.writerow(['id', 'Names', 'ScreenNames', 'Tweets', 'Tweets After Clean', 'Predictions'])
	            i = 0
	            while i < len(listOfTweets):
	            	spamwriter.writerow([listOfIds[i], listOfNames[i] ,listOfScreenNames[i], listOfTweets[i], testTweets[i+1], res[i]])
	            	i = i+1
	            break
	        except EOFError:
	            break

if __name__ == '__main__':
	#loads data from tweets.pkl file
	data = loadData()

	#parse this data
	listOfTweets, listOfIds, listOfScreenNames, listOfNames = parseTweet(data)

	#write it to the csv file
	writeToCSV(listOfTweets, listOfIds, listOfScreenNames, listOfNames)

	#Step 1 is to clean the tweets based on several cleaning parameters
	cleanedTweets,sentiment,testTweets = fetchTrainTestStop()

	# Take the cleaned tweets and build a training model , the first classifier that will be used is the decision tree classifier
	testTweets,res = predictTweets(cleanedTweets,sentiment,testTweets)

	#write it to the final csv file
	write(listOfTweets, listOfIds, listOfScreenNames, listOfNames, testTweets, res)

