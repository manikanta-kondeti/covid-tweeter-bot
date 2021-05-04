from flask import Flask
from flask_apscheduler import APScheduler
import time
import schedule


from src import search_tweets

app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello World!"

@app.route("/tweets")
def search_for_tweets():
    return ""


@app.route('/run-tasks')
def run_tasks():
    return 'Scheduled several long running tasks.', 200


def scheduled_task():
    time.sleep(2)
    search_tweets.execute()


schedule.every(590).seconds.do(scheduled_task)


if __name__ == "__main__":
    while True:
        schedule.run_pending()
        time.sleep(1)
