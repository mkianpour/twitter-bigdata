#import boto3
import tweepy
import csv
import os

def lambda_handler(event, context):
    ####input your credentials here
    consumer_key = os.environ['CONSUMER_AUTH_KEY']
    consumer_secret = os.environ['CONSUMER_AUTH_SECRET']
    access_token = os.environ['ACCESS_TOKEN']
    access_token_secret = os.environ['ACCESS_SECRET']

    hashtag = os.environ['HASHTAG']

    auth = tweepy.AppAuthHandler(consumer_key, consumer_secret)
    # auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth,wait_on_rate_limit=True,wait_on_rate_limit_notify=True)
    #####United Airlines
    # Open/Create a file to append data
    csvFile = open('aws_hashtag.csv', 'a')
    #Use csv Writer
    csvWriter = csv.writer(csvFile)

    hashtag_entry = f"#{hashtag}"
    print (hashtag_entry)
    for tweet in tweepy.Cursor(api.search,q=hashtag_entry,count=100,
                               since="2018-12-31").items():
        print (tweet.created_at, tweet.text)
        csvWriter.writerow([tweet.created_at, tweet.text.encode('utf-8')])

lambda_handler("","")
