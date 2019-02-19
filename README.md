# twitter-machine-learning
working with AWS to implement some use cases for twitter data
In most of functions the followings should be set as Env Variables in Lambda functions:
`CONSUMER_AUTH_KEY`
`CONSUMER_AUTH_SECRET`
`ACCESS_TOKEN`
`ACCESS_SECRET`


## hashtag_collector.py
Uses Search API provided by Twitter to collect tweets with a specified hashtag.
hashtag can be defined using Env Variable `HASHTAG`
