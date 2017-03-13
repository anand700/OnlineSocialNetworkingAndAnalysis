*****************************************************************
Introduction
*****************************************************************
Open-ended exploration of online social networking.
*****************************************************************

The goal is to analyze how the users have tweeted about Best Buy by using the screen name: #bestbuy. This is done by collecting users and their tweets, detecting communities by calculating the betweenness and classifying the tweets by sentiment analysis.

Commands to run:
```
python collect.py
python cluster.py
python classify.py
python summarize.py
```

collect.py: The data is collected using the screen name: #bestbuy. The data is raw and is directly from the original source. Running this script creates a file or files containing the data that is needed for the subsequent phases of analysis.

cluster.py: This reads the data collected in the previous step and uses community detection algorithm to cluster users into communities. This also writes to files to save the results.

classify.py: Classifies the data by detecting the sentiment. This also writes to files to save the results.

summarize.py: Summarizes all the steps above by showing the following:

Number of users collected

Number of messages collected

Number of communities discovered

Average number of users per community

Number of instances per class found

One example from each class
