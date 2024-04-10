import os

import pandas as pd
import tweepy
import config as config

# import boto3

bucket_name = 'kishlay-airflow-twitter-project'


def run_twitter_etl():
    # Twitter authentication
    twitter_client = tweepy.Client(bearer_token=config.BearerToken,
                                   consumer_key=config.ConsumerKey,
                                   consumer_secret=config.ConsumerSecret,
                                   access_token=config.AccessKey,
                                   access_token_secret=config.AccessSecret)

    # Fetch user data
    user = twitter_client.get_user(username='Nick_Offerman').data

    # Extract the user id and user name
    user_id = user.id
    user_name = user.name

    # Fetch tweets by the user
    tweets = twitter_client.get_users_tweets(id=user_id,
                                             max_results=50,
                                             tweet_fields=['id',
                                                           'text',
                                                           'created_at',
                                                           'public_metrics']
                                             )

    tweets_list = []
    for tweet in tweets.data:
        refined_tweet = {'user': user_name,
                         'username': user,
                         'text': tweet.text,
                         'like_count': tweet.public_metrics['like_count'],
                         'reply_count': tweet.public_metrics['reply_count'],
                         'retweet_count': tweet.public_metrics['retweet_count'],
                         'created_at': tweet.created_at}

        tweets_list.append(refined_tweet)

    # Create DataFrame from tweets list
    df = pd.DataFrame(tweets_list)

    # # Save DataFrame to S3
    # s3 = boto3.client('s3',
    #                   aws_access_key_id=config.KEY,
    #                   aws_secret_access_key=config.SECRET)

    csv_buffer = df.to_csv(None).encode()

    # s3.put_object(Bucket=bucket_name,
    #               Key='refined_tweets.csv',
    #               Body=csv_buffer)

    file_path = "./data/tweets.csv"
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "wb") as file:
        file.write(csv_buffer)
    print(f"CSV file saved to {file_path}")


run_twitter_etl()
