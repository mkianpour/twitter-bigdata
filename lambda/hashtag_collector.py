import boto3
import tweepy
import csv
import os
import datetime

def lambda_handler(event, context):
    ####input your credentials here
    consumer_key = os.environ['CONSUMER_AUTH_KEY']
    consumer_secret = os.environ['CONSUMER_AUTH_SECRET']
    access_token = os.environ['ACCESS_TOKEN']
    access_token_secret = os.environ['ACCESS_SECRET']

    hashtag = os.environ['HASHTAG']
    # hashtag = event["hashtag"]
    datalake_bucket = os.environ['DATALAKE_BUCKET']

    auth = tweepy.AppAuthHandler(consumer_key, consumer_secret)
    # auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth,wait_on_rate_limit=True,wait_on_rate_limit_notify=True)
    # Open/Create a file to append data
    csvFile = open('/tmp/hashtag.csv', 'a')
    #Use csv Writer
    csvWriter = csv.writer(csvFile)

    hashtag_entry = f"#{hashtag}"
    s3 = boto3.resource('s3')

    yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
    y_day = yesterday.strftime("%Y-%m-%d")
    print ("y_day: ", y_day, " yesterday: ", yesterday)

    for tweet in tweepy.Cursor(api.search,q=hashtag_entry,count=100,
                               since=y_day).items():
        csvWriter.writerow([hashtag,
                            tweet.user.name,
                            tweet.created_at,
                            tweet.text.encode('utf-8')])
    now = datetime.datetime.now()
    now_dir = now.strftime("%Y-%m-%d")
    s3.Bucket(datalake_bucket).upload_file("/tmp/hashtag.csv",
                                            f"twitter-data/hashtags/{hashtag}/{now_dir}/hashtag.csv")
