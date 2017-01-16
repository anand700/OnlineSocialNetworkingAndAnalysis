"""
cluster.py
"""
from collections import Counter, defaultdict, deque
import copy
import math
import pickle
import networkx as nx
import urllib.request
import matplotlib.pyplot as plt
import sys
import time
import itertools
import re
import csv
from TwitterAPI import TwitterAPI

consumer_key = 'aqWQzq1T0xLrSfxJHD7FhvJgF'
consumer_secret = '1gFIH1TGGFfJG9YxizUau2KBguV84Xds0IZwJ0saL20JIduU91'
access_token = '769178823468408832-jnMZxvAWvcKWZeVrMvWoPnzPa8SekEn'
access_token_secret = 'YPPt5Y2gIrscrqbul3jp9H1YPRR2As4XE34abQK6IXDfh'

## Community Detection
def robust_request(twitter, resource, params, max_tries=2):
    """ 
    Returns:
      A TwitterResponse object, or None if failed.
    """
    for i in range(max_tries):
        request = twitter.request(resource, params)
        if request.status_code == 200:
            return request
        else:
            print('Got error %s \nsleeping for 15 minutes.' % request.text)
            sys.stderr.flush()
            time.sleep(61 * 15)



def count_friends(users):
    c = Counter()
    for usrs in users: 
    	c.update(usrs['friends'])
    return c


def friend_overlap_modified(users, g):
    twitter = get_twitter()
    screen_names = ["BestBuy"]
    mainUsers = get_users(twitter, screen_names)
    mainusers = mainUsers.json()
    # g.add_edge("BestBuy","amazon")
    combination = []
    friendOverlap = []
    for usrs1 in users:
    	for usrs2 in users:
    		if usrs1['screen_name'] != usrs2['screen_name'] and usrs2['screen_name']+usrs1['screen_name'] not in combination:
    			combination.append(usrs1['screen_name']+usrs2['screen_name'])
    			c = calculateOverlapOfFriends(usrs1, usrs2)
    			friendOverlap.append((usrs1['screen_name'], usrs2['screen_name'], c))
    			g.add_edge(usrs1['screen_name'],usrs2['screen_name'])
    			if mainusers[0]['id'] in usrs1['friends']:
    				# print("edge between user1 and bestbuy")
    				g.add_edge("BestBuy",usrs1['screen_name'])
    			if mainusers[0]['id'] in usrs2['friends']:
    				# print("edge between user2 and bestbuy")
    				g.add_edge("BestBuy",usrs2['screen_name'])

    return sorted(friendOverlap,key=lambda x: -x[2])


def readGraph():
    g = nx.Graph()
    listOfEdges = createEdges(g)
    return g

def get_twitter():
    """ 
    Returns:
      An instance of TwitterAPI.
    """
    return TwitterAPI(consumer_key, consumer_secret, access_token, access_token_secret)

def createEdges(g):
	 # print("createEdges>>")
	 twitter = get_twitter()
	 unpickleds = readPickleFile()
	 screen_names = list(getScreenNames(unpickleds))
	 # print(len(screen_names))
	 with open('users.pkl', 'rb') as f:
	    while True:
	        try:
	            users = pickle.load(f)
	        except EOFError:
	            break
	 # users = sorted(get_users(twitter, screen_names), key=lambda x: x['screen_name'])
	 # print('found %d users with screen_names %s' % (len(users), str([u['screen_name'] for u in users])))
	 # add_all_friends(twitter, users, g)
	 # add_all_friends(twitter, users)
	 # print('Friends per candidate:')
	 # print_num_friends(users)
	 # friend_counts = count_friends(users)
	 # print('Most common friends:\n%s' % str(friend_counts.most_common(5)))
	 friend_overlap_modified(users,g)


	 # print('Friend Overlap:\n%s' % str(friend_overlap(users)))
	 # print('User followed by Hillary and Donald: %s' % followed_by_hillary_and_donald(users, twitter))
	 # graph = create_graph(users, friend_counts)
	 # print('graph has %s nodes and %s edges' % (len(graph.nodes()), len(graph.edges())))
	 # draw_network(graph, users, 'network.png'

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

def get_users(twitter, screen_names):
    users = robust_request(twitter, 'users/lookup', {'screen_name' : screen_names})
    return users


def readPickleFile():
	unpickleds = []
	with open('tweets.pkl', 'rb') as f:
	    while True:
	        try:
	            unpickleds = pickle.load(f)
	        except EOFError:
	            break
	return unpickleds


def getScreenNames(unpickleds):
	screen_names = set()
	for unpickled in unpickleds:
		screen_names.add(unpickled['user']['screen_name'])
	return screen_names



def getBetweenness(G0):
        eb = nx.edge_betweenness_centrality(G0)
        return sorted(eb.items(), key=lambda x: x[1], reverse=True)

def partitionGirvanNewman(graph, k):
	#copy graph
	 duplicateGraph = graph.copy()

	 #remove edges
	 edge_to_remove = deque(getBetweenness(duplicateGraph))

	 #components
	 components = list(nx.connected_component_subgraphs(duplicateGraph))

	 while len(components) < k:
	 	edge = edge_to_remove.popleft()
	 	# print([edge])
	 	for u,v in [edge]:
	 		duplicateGraph.remove_edge(*u)
	 		
	 	components = list(nx.connected_component_subgraphs(duplicateGraph))

	 return components

def writeToCSV(clusters):
	with open('clusters.csv', 'w') as f:
	    while True:
	        try:
	            spamwriter = csv.writer(f)
	            spamwriter.writerow(['Cluster Id', 'Number of Nodes'])
	            i = 0
	            while i < len(clusters):
	            	spamwriter.writerow([i, len(clusters[i])])
	            	i = i+1
	            break
	        except EOFError:
	            break


def main():
    graph = readGraph()
    # plt.figure(figsize=(15,15))
    # nx.draw_networkx(graph,node_size=100,alpha=0.5,width=0.1)
    # plt.axis('off')
    # plt.savefig('clusterNetwork.png')
    clusters = partitionGirvanNewman(graph, 20)
    writeToCSV(clusters)
    for i in range(0,len(clusters)):
    	print('cluster : ',i)
    	print('with number of nodes : ',len(clusters[i]))
    	print(clusters[i].nodes())



if __name__ == '__main__':
    main()
