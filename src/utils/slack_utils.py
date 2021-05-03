import json
import requests
from src.utils.basics import read_variable_from_file


class SlackUtils:

    def __init__(self):
        self.slack_url = read_variable_from_file("slack_url")

    def post_message(self, slack_data):
        data = json.dumps(slack_data)
        response = requests.post(self.slack_url, data=data, headers={'Content-Type': 'application/json'})
        if response.status_code != 200:
            raise False
