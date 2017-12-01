# import necessary packages
import os
import time
import tweepy
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from datetime import datetime
import seaborn as sns
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
analyzer = SentimentIntensityAnalyzer()

api_key = os.getenv('api_key')
api_sec = os.getenv('api_sec')
token = os.getenv('token')
token_sec = os.getenv('token_sec')

# Setup Tweepy API Authentication
auth = tweepy.OAuthHandler(api_key, api_sec)
auth.set_access_token(token, token_sec)
api = tweepy.API(auth, parser=tweepy.parsers.JSONParser())

def new_ids(last_id):
    #looks for new mentions & creates a list of the accounts to analyze & those to attribute

    # Search for all tweets
    public_tweets = api.search("@plot_kb", count=100, result_type="recent", since_id=last_id)

    # First, check if there are any new tweets
    if public_tweets["statuses"]:
    
        # create empty lists to store screen names
        to_plot = []
        to_attribute = []

        # loop through the tweets & store the screen names of the account to be analyzed &
        # the account that requested the analysis (only 1 analysis per mention)
        for tweet in public_tweets['statuses']:
            for mention in tweet['entities']['user_mentions']:
                if mention['screen_name'] != 'plot_kb':
                    plot_name = mention['screen_name']
                    to_attribute.append(tweet['user']['screen_name'])
                    to_plot.append(plot_name)
                    break
        if len(to_plot) > 0:
            return({"to_plot": to_plot, "to_attribute": to_attribute})
        else:
            return([last_id])
    else:
        return([last_id])

def tweet_sentiment(target_user, attribution):
    # plot the sentiment analysis of the target user's last 500 tweets
    
    try:
        compound_list = []
        
        #Loop through 25 pages of tweets (total 500 tweets)
        for x in range(25):

            # Get all tweets from home feed
            public_tweets = api.user_timeline(target_user, page=x)  
            
            # Loop through all tweets
            for tweet in public_tweets:

                # Run Vader Analysis on each tweet
                results = analyzer.polarity_scores(tweet["text"])

                # Add each compound score to the compound_list
                compound_list.append(results["compound"])

        # create an array of the tweet index from 0 to -499
        tweet_no = sorted(np.arange(-len(compound_list), 0), reverse = True)
    
        # average the compound score
        avg_score = round(np.mean(compound_list),2)
        
        # create a plot of the compound score for each tweet
        sns.set_style("darkgrid")
        plt.plot(tweet_no, compound_list, color = 'k', marker = '.', lw=.5)
        plt.plot([-len(compound_list), 0], [avg_score, avg_score], color = 'm', linewidth=2)
        lgd = plt.legend(labels = ['tweet score', f'avg score ({avg_score})'], title = 'Legend', bbox_to_anchor=(1,1))
        current_date = datetime.strftime(datetime.now(), '%m/%d/%y')
        plt.ylim(-1, 1)
        plt.xlabel("Tweets Ago")
        plt.ylabel("Tweet Polarity")
        plt.title(f"Sentiment Analysis of @{target_user} Tweets ({current_date})")

        # save the plot to a file
        filename = f"plots\\{target_user}_{datetime.strftime(datetime.now(),'%Y%m%d%H%M%S')}.png"
        plt.savefig(filename, bbox_extra_artists=(lgd,), bbox_inches='tight', dpi = 300)
        plt.close()
        
        # reset compound list & avg_score
        compound_list = []
        avg_score = ""
        
        # tweet out the plot
        api.update_with_media(os.path.join('C:\\Users\\Kali\\repo\\twitter-plot-kb\\', filename),
                              f"Tweet sentiment analysis for @{target_user} as requested by @{attribution}")
    except:
        api.update_status(f"@{attribution} sorry, there was an error with the analysis of @{target_user}. I'll look into it and try to let you know why.")


my_tweets = api.user_timeline('plot_kb', count = 100)
last_id = my_tweets[0]['id']

# every 5 minutes, scan for new mentions & update with plots
while True:
    
    print(f"starting analysis at {datetime.strftime(datetime.now(),'%d-%m-%Y %H:%M:%S')}")
    
    new = new_ids(last_id)
    
    if type(new) == dict:
        
        df = pd.DataFrame(new)
            
        recently_analyzed = []
        
        my_tweets = api.user_timeline('plot_kb', count = 100)
        print('analyzing previous tweets')
        for tweet in my_tweets:
            try:
                user = tweet['entities']['user_mentions'][0]['screen_name']
                recently_analyzed.append(user)
            except IndexError:
                print('1 tweet has no mentions')
        print('finished analyzing previous tweets')
        
        for index, row in df.iterrows():
            if row['to_plot'] not in recently_analyzed:
                print(f"analyzing {row['to_plot']}")
                tweet_sentiment(row['to_plot'], row['to_attribute'])
                recently_analyzed.append(row['to_plot'])
                print(f"finished analyzing {row['to_plot']}")
            else:
                print(f"{row['to_plot']} was already analyzed recently, skipping")
        
        my_tweets = api.user_timeline('plot_kb', count = 100)
        last_id = my_tweets[0]['id']
        print('Done analyzing new tweets. Going to sleep for 5 minutes. Zzzzz....\n')
        time.sleep(300)
    else:
        print('No new tweets to analyze. Going to sleep for 5 minutes. Zzzzz....\n')
        time.sleep(300)