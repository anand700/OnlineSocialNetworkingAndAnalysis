"""
sumarize.py
"""
"""
collect.py
"""
from collections import Counter
import matplotlib.pyplot as plt
import networkx as nx
import sys
import time
import itertools
import pymysql
import re
import pickle
import csv
from TwitterAPI import TwitterAPI

def getNoOfUsers():
	unpickleds = []
	with open('users.pkl', 'rb') as f:
	    while True:
	        try:
	            unpickleds = pickle.load(f)
	        except EOFError:
	            break
	return len(unpickleds)


def getNoOfTweets():
	unpickleds = []
	with open('tweets.pkl', 'rb') as f:
	    while True:
	        try:
	            unpickleds = pickle.load(f)
	        except EOFError:
	            break
	return len(unpickleds)


def readClusterCSV():
    with open('clusters.csv', 'r') as f:
        while True:
            try:
                spamreader = csv.reader(f)
                sumOfClusterNodes = 0
                count = 0
                for data in spamreader:
                    if data[1] != "Number of Nodes":
                        sumOfClusterNodes = sumOfClusterNodes + int(data[1])
                    count = count + 1
                Average = sumOfClusterNodes/(count-1)
                return count-1, Average
                break
            except EOFError:
                break


def readAfterClassifyCSV():
    with open('AfterClassify.csv', 'r') as f:
        while True:
            try:
                spamreader = csv.reader(f)
                numberPositiveInstance = 0
                numberNegativeInstance = 0
                instances = dict()
                instances['tweet'] = []
                instances['value'] = []
                instances['sentiment'] = []
                count = 0
                for data in spamreader:
                    if data[4] != "Tweets After Clean":
                        if count == 51:
                            instances['tweet'].append(data[3])
                            instances['value'].append(data[5])
                            # print(data[3])
                            # print(data[5])
                            if data[5] != "0":
                                # print("data[5]  not 1")
                                instances['sentiment'].append("Positive")
                            else:
                                # print("data[5]  1")
                                instances['sentiment'].append("Nagative")
                        if count == 50:
                            instances['tweet'].append(data[3])
                            instances['value'].append(data[5])
                            # print(data[3])
                            # print(data[5])
                            if data[5] != "0":
                                # print("data[5]  not 1")
                                instances['sentiment'].append("Positive")
                            else:
                                # print("data[5] 1")
                                instances['sentiment'].append("Nagative")
                        if data[5] != "0":
                            numberPositiveInstance = numberPositiveInstance + 1
                        else:
                            numberNegativeInstance = numberNegativeInstance + 1
                    count = count + 1
                return numberPositiveInstance, numberNegativeInstance, instances
                break
            except EOFError:
                break


def main():
    numbOfUsers = getNoOfUsers()
    numbOfTweets = getNoOfTweets()
    print("Number of unique users collected : "+str(numbOfUsers))
    print("Number of unique messages collected : "+str(numbOfTweets))
    numberOfCommunities, Average = readClusterCSV()
    print("Number of communities discovered : "+str(numberOfCommunities))
    print("Average number of users per community : "+str(Average))
    print("-----Note: Please change max_features as required which is an input to CountVectorize if you are running collect.py-----")
    print("-----For training the tweets i have used train.csv-----")
    numberPositiveInstance, numberNegativeInstance, instances = readAfterClassifyCSV()
    print("Number of Positive instances found : "+str(numberPositiveInstance))
    print("Number of Negative instances found : "+str(numberNegativeInstance))
    print("One example from each class : ")
    for i in range(0,len(instances)-1):
        print("tweets : ",instances['tweet'][i])
        print("values : ",instances['value'][i])
        print("sentiment : ", instances['sentiment'][i])
        print("---------")

    

	    
if __name__ == '__main__':
    main()

# That's it for now! This should give you an introduction to some of the data we'll study in this course.
