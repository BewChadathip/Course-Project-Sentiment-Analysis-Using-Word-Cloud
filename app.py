from flask import Flask, render_template,request
import tweepy
import configparser
import pymongo
from pprint import pprint
import numpy as np
from wordcloud import WordCloud, STOPWORDS
import pythainlp
from pythainlp import word_tokenize

#object of Flask
app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/sendData')
def signupForm():
    keyworld = request.args.get('keyworld')
    twitterAPI(keyworld)
    return render_template("thankyou.html",data = {"keyworld": keyworld})

def twitterAPI(keyworld):
    # read configs
    config = configparser.ConfigParser()
    config.read('config.int')

    api_key = config['twitter']['api_key']
    api_key_secret = config['twitter']['api_key_secret']

    access_token = config['twitter']['access_token']
    access_token_secret = config['twitter']['access_token_secret']

    # authentication
    auth = tweepy.OAuthHandler(api_key, api_key_secret)
    auth.set_access_token(access_token, access_token_secret)

    api = tweepy.API(auth)

    #connect database
    try:
        client = pymongo.MongoClient('mongodb://localhost:27017')
    except Exception:
        print("Error:" + Exception)
    #create a database
    db = client['twitter_DB']# use or create a database named pymongo_demo

    #create a collection
    tweet_collection = db['tweet_collection']
    # make sure the collected tweets are unique
    tweet_collection.create_index([("id", pymongo.ASCENDING)],unique = True) 

    # search tweets
    keywords = keyworld
    limit=300

    tweets = tweepy.Cursor(api.search_tweets, q=keywords, count=100, tweet_mode='extended').items(limit)

    #delete data in collection before get new
    tweet_collection.delete_many({})
    
    #insert each tweet to collection
    for tweet in tweets:
        try:
            tweet_collection.insert_one(tweet._json)
            # print the date of the collected tweets
            pprint(tweet['created_at'])
        except:
            pass

    #Check that if data is stored in Mongo
    # then retrieve the data to show in the back end(in Terminal).
    tweet_cursor = tweet_collection.find()
    user_cursor = tweet_collection.distinct("user.id")
    print(len(user_cursor))

    document= open("document.txt","w")
    for extract in tweet_cursor:
        try:
            print('-----')
            print('name:-',extract["user"]["name"])
            print('text:-',extract["full_text"])
            print('Created Date:-',extract["created_at"])
            # document.append(str(extract["full_text"]))
            document.write(str(extract["full_text"]))
        except:
            print("Error in Encoding")
            pass
    
    readfile= open("document.txt","r")
    words = word_tokenize(readfile.read())
    all_words = ' '.join(words).lower()
    document.close

    stopwords = set(STOPWORDS)
    stopwords.update(["RT", "https", "t", "s", "charles iii", "iii", "paulineblack", "co", "pauline", "paulineblackOBE", "amp", "obe", "black", "afor32977890", "de", "le"])

    x, y = np.ogrid[:300, :500]

    mask = x*y
    mask = 255 * mask.astype(int)

#Creat word cloud
    wc = WordCloud(font_path="/Users/bewchadathip/Documents/Sentiment Analysis Project.py/font_path/Fahkwang-Medium.ttf", regexp='[a-zA-Z0-9ก-๙]+', background_color="black", repeat=True, mask=mask, stopwords=stopwords,max_words=150)
    wc.generate(all_words)
    wc.to_file("/Users/bewchadathip/Documents/Sentiment Analysis Project.py/static/test.jpg")


if __name__ == "__main__":
    app.run()