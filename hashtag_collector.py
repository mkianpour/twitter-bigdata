import boto3
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
    datalake_bucket = os.environ['DATALAKE_BUCKET']

    auth = tweepy.AppAuthHandler(consumer_key, consumer_secret)
    # auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth,wait_on_rate_limit=True,wait_on_rate_limit_notify=True)
    #####United Airlines
    # Open/Create a file to append data
    csvFile = open('/tmp/aws_hashtag.csv', 'a')
    #Use csv Writer
    csvWriter = csv.writer(csvFile)

    hashtag_entry = f"#{hashtag}"
    s3 = boto3.resource('s3')
    csvWriter.writerow(["created_at", "tweet_context"])
    for tweet in tweepy.Cursor(api.search,q=hashtag_entry,count=100,
                               since="2018-12-31").items():
        csvWriter.writerow([tweet.created_at, tweet.text.encode('utf-8')])
    s3.Bucket(datalake_bucket).upload_file("/tmp/aws_hashtag.csv",
                                            f"twitter-data/hashtags/{hashtag}/aws_hashtag.csv")