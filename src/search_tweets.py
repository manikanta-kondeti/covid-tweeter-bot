import time

import requests
import json

from src.utils.basics import read_variable_from_file
from src.utils.slack_utils import SlackUtils


def auth():
    tokens_file = open("tokens.json")
    x = json.load(tokens_file)
    print(x)
    return x["bearer_token"]


def create_url(search_query):
    query = search_query
    # Tweet fields are adjustable.
    # Options include:
    # attachments, author_id, context_annotations,
    # conversation_id, created_at, entities, geo, id,
    # in_reply_to_user_id, lang, non_public_metrics, organic_metrics,
    # possibly_sensitive, promoted_metrics, public_metrics, referenced_tweets,
    # source, text, and withheld
    tweet_fields = "tweet.fields=author_id"
    url = "https://api.twitter.com/2/tweets/search/recent?query={}&{}".format(
        query, tweet_fields
    )
    return url


def create_headers(bearer_token):
    headers = {"Authorization": "Bearer {}".format(bearer_token)}
    return headers


def connect_to_endpoint(url, headers):
    response = requests.request("GET", url, headers=headers)
    print(response.status_code)
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
    return response.json()

# tweet format: https://twitter.com/<author_id>/status/<conversation_id>


def execute():
    medicines = read_variable_from_file("medicines")
    cities = read_variable_from_file("cities")

    tuples = construct_searchable_terms(medicines, cities)

    for tup in tuples:
        time.sleep(3)
        search_query = tup[0] + " " + tup[1]
        tweets = fetch_tweet(search_query)
        analyse_tweets(tweets)


def construct_searchable_terms(medicines, cities):

    list_of_tuples = []
    for i in medicines:
        for j in cities:
            list_of_tuples.append((i, j))

    return list_of_tuples


def fetch_tweet(search_query):
    bearer_token = auth()
    url = create_url(search_query)
    headers = create_headers(bearer_token)

    json_response = connect_to_endpoint(url, headers)
    print(json.dumps(json_response, indent=4, sort_keys=True))
    return json_response


def analyse_tweets(tweets):
    for tweet in tweets["data"]:
        author_id = tweet["author_id"]
        conversation_id = tweet["id"]

        payload = {"channel": "#covid19-tweets-findudaan", "username": "covid-tweet-helper-bot",
                   "text": " https://twitter.com/{}/status/{} ".format(author_id, conversation_id), "icon_emoji": ":mask:"}
        slack_utils = SlackUtils()
        slack_utils.post_message(payload)
