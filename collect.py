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
from TwitterAPI import TwitterAPI

consumer_key = 'aqWQzq1T0xLrSfxJHD7FhvJgF'
consumer_secret = '1gFIH1TGGFfJG9YxizUau2KBguV84Xds0IZwJ0saL20JIduU91'
access_token = '769178823468408832-jnMZxvAWvcKWZeVrMvWoPnzPa8SekEn'
access_token_secret = 'YPPt5Y2gIrscrqbul3jp9H1YPRR2As4XE34abQK6IXDfh'


listOfTweets = []
setOfScreenNames = set()
listOfScreenNames = []

def get_users(twitter, screen_names):
    users = robust_request(twitter, 'users/lookup', {'screen_name' : screen_names})
    return users

def get_user_by_id(twitter, id):
    request = robust_request(twitter, 'users/lookup', {'user_id' : id})
    user = request.json()
    return user[0]['screen_name']


def get_friends(twitter, screen_name):
    request = robust_request(twitter, 'friends/ids', {'screen_name' : screen_name, 'count' : 5000, 'cursor' : -1})
    #type (sorted(request['ids']))
    friends = request.json()
    return sorted(friends['ids'])


def add_all_friends(twitter, users):
    for usrs in users:
    	friends = get_friends(twitter, usrs['screen_name'])
    	usrs.update({'friends':friends})

def print_num_friends(users):
    for usrs in users:
    	print(usrs['screen_name'], ' : ' ,len(usrs['friends']))


def count_friends(users):
    c = Counter()
    for usrs in users: 
    	c.update(usrs['friends'])
    return c
    

def friend_overlap(users):
    combination = []
    friendOverlap = []
    for usrs1 in users:
    	for usrs2 in users:
    		if usrs1['screen_name'] != usrs2['screen_name'] and usrs2['screen_name']+usrs1['screen_name'] not in combination:
    			combination.append(usrs1['screen_name']+usrs2['screen_name'])
    			friendOverlap.append((usrs1['screen_name'], usrs2['screen_name'], calculateOverlapOfFriends(usrs1, usrs2)))
    return sorted(friendOverlap,key=lambda x: -x[2])
    
def calculateOverlapOfFriends(user1, user2):
    users = []
    c = Counter()
    N = 0
    users.append(user1)
    users.append(user2)
    
    c = count_friends(users)
    
    for value in c.values():
    	if value == 2:
    		N += 1
    c.clear()
    users.clear()
    return N



def create_graph(users, friend_counts):
    friends = []
    for friend in friend_counts:
    	if friend_counts[friend] > 1:
    		friends.append(friend)
    graph = nx.DiGraph()
    for user in users:
        graph.add_node(user['screen_name'])
        for f in friends:
        	if f in user['friends']:
        		graph.add_node(f)
        		graph.add_edge(user['screen_name'], f)
    #nx.draw(graph, with_labels=False)
    return graph


def getLabelsOfCandidates(users):
    """
    Gets the labels of all candidates.
    """
    return dict([tuple([x['screen_name'],x['screen_name']]) for x in users])

def draw_network(graph, users, filename):
    labels = getLabelsOfCandidates(users)
    pos = nx.spring_layout(graph)
    plt.figure(figsize=(15,15))
    nx.draw_networkx(graph,node_size=100,alpha=0.5,labels=labels,width=0.1)
    plt.axis('off')
    plt.savefig(filename)

def get_twitter():
    return TwitterAPI(consumer_key, consumer_secret, access_token, access_token_secret)


def get_timeline():
    tweets = []
    twitter = get_twitter()
    screen_name = '#bestbuy'
    request = robust_request(twitter, 'search/user_timeline', {'screen_name' : screen_name, 'count' : 200})
    tweets = request
    return tweets

def get_tweets():
    twitter = get_twitter()
    hashTagName = '#bestbuy'
    tweets = robust_request(twitter, 'search/tweets', {'q' : hashTagName, 'count' : 180})
    return tweets


def getMatchedProducts():
    dealMatchedGauranteed = []
    productsMatched = set()
    listOfProducts = getProductNameList()
    timeline = get_timeline()
    for product in listOfProducts:
        for tweet in timeline:
            deal = (tweet['text']).encode('ascii','ignore')
            if(len(re.findall('\s'+product+'\s', deal.decode("utf-8"))) >= 1):
                productsMatched.add(product)
                dealMatchedGauranteed = dealMatchedGauranteed + [deal.decode("utf-8").replace('\n',' ')]
    return dealMatchedGauranteed,productsMatched

def robust_request(twitter, resource, params, max_tries=2):
    for i in range(max_tries):
        request = twitter.request(resource, params)
        if request.status_code == 200:
            return request
        else:
            print('Got error %s \nsleeping for 15 minutes.' % request.text)
            sys.stderr.flush()
            time.sleep(61 * 15)

def parseTweet(tweets):
       myListForTweet = []
       for tweet in tweets:
	       # myListForTweet['screen_name'] = tweet['user']['screen_name']
	       # myListForTweet['user_name'] = tweet['user']['name']
	       # myListForTweet['desc'] = tweet['user']['description']
	       # myListForTweet['text'] = tweet['text']
	       setOfScreenNames.add(tweet['user']['screen_name'])
	       listOfTweets.append(tweet['text'])
	       myListForTweet.append(tweet)
       return myListForTweet



def main():
    """ Main method. You should not modify this. """
    twitter = get_twitter()
    tweets = get_tweets()
    myListForTweet = parseTweet(tweets)
    # print(listOfDict)
    pickle.dump(myListForTweet, open('tweets.pkl', 'wb'))
    screen_names = list(setOfScreenNames)
    print('Established Twitter connection.')
    # print('Read screen names: %s' % screen_names)
    print(len(screen_names))
    users = sorted(get_users(twitter, screen_names[:10]), key=lambda x: x['screen_name'])
    print('found %d users with screen_names %s' %
          (len(users), str([u['screen_name'] for u in users])))
    add_all_friends(twitter, users)
    print('Friends per candidate:')
    print_num_friends(users)
    friend_counts = count_friends(users)
    print('Most common friends:\n%s' % str(friend_counts.most_common(5)))
    print('Friend Overlap:\n%s' % str(friend_overlap(users)))
    graph = create_graph(users, friend_counts)
    print('graph has %s nodes and %s edges' % (len(graph.nodes()), len(graph.edges())))
    draw_network(graph, users, 'network.png')
    print('network drawn to network.png')

    

	    
if __name__ == '__main__':
    main()

# That's it for now! This should give you an introduction to some of the data we'll study in this course.
