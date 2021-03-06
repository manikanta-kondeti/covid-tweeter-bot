import time
import requests
import json
from src.utils.basics import read_variable_from_file
from src.utils.slack_utils import SlackUtils
from datetime import datetime, timedelta


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
    tweet_fields = "tweet.fields=author_id,conversation_id"
    now = datetime.now()
    now_minus_10 = now - timedelta(minutes=340)
    start_time = now_minus_10.isoformat("T", "milliseconds") + "Z"
    url = "https://api.twitter.com/2/tweets/search/recent?query={}&{}&start_time={}".format(
        query, tweet_fields, start_time
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
    requirement_strings = read_variable_from_file("requirement_strings")

    for city in cities:
        time.sleep(5)
        search_query = city + " " + get_medicines(medicines) + " " + get_requirement_strings(requirement_strings) + ' -"VERIFIED"'
        tweets = fetch_tweet(search_query)
        analyse_tweets(tweets)


def get_requirement_strings(requirement_strings):
    return "(" + " OR ".join(requirement_strings) + ")"


def get_medicines(meds):
    med_or_string = "("
    for med in meds:
        med_or_string += med + " OR "

    med_or_string += "fabiflu)"
    return med_or_string


def fetch_tweet(search_query):
    bearer_token = auth()
    url = create_url(search_query)
    headers = create_headers(bearer_token)

    json_response = connect_to_endpoint(url, headers)
    print(json.dumps(json_response, indent=4, sort_keys=True))
    return json_response


def analyse_tweets(tweets):
    if (tweets["meta"]["result_count"] == 0):
        return
    for tweet in tweets["data"]:
        author_id = tweet["author_id"]
        id = tweet["id"]

        if "RT @" in tweet["text"]:
            continue

        payload = {"channel": "#covid19-tweets-warroom", "username": "covid-tweet-listener-bot",
                   "text": " https://twitter.com/{}/status/{} ".format(author_id, id), "icon_emoji": ":mask:"}
        slack_utils = SlackUtils()
        slack_utils.post_message(payload)
