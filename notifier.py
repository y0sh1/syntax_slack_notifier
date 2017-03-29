from slackclient import SlackClient
import urllib.request
from configparser import ConfigParser
from ics import Calendar
import arrow
from datetime import timedelta
from datetime import datetime

class Notifier:

    slack_token = ""

    def __init__(self, slack_token):
        self.slack_token = slack_token

    def notify(self, messages):
        slack = SlackClient(token=self.slack_token)
        for message in messages:
            slack.api_call(
                "chat.postMessage",
                username="Syntax Event Bot",
                icon_emoji=":calendar:",
                channel="#testing",
                text=message
            )

    def notify_events(self, events):
        for event in events:
            self.notify([event.name + " begint om " + str(event.begin.datetime)])

class Events:

    events_url = ""

    def __init__(self, events_url):
        self.events_url = events_url

    def get_events(self):
        calendar = Calendar(urllib.request.urlopen(self.events_url).read().decode('iso-8859-1'))
        return calendar.events

    def get_future_events(self, this_week = False):
        events = self.get_events()
        future_events = []
        current_time = arrow.utcnow()
        this_monday = current_time.replace(days=-(current_time.weekday()), hour=0, minute=0, second=0, microsecond=0)
        this_sunday = current_time.replace(days=+(6-(current_time.weekday())), hour=23, minute=59, second=59, microsecond=0)
        for unique_event in events:
            if this_week and unique_event.begin >= this_monday and unique_event.end <= this_sunday:
                future_events.append(unique_event)
            elif unique_event.begin.datetime >= current_time and not this_week:
                future_events.append(unique_event)
        return future_events

if __name__ == "__main__":
    config = ConfigParser()
    config.read('config.ini')
    syntax_events = Events(config['syntax']['calendar_url']).get_future_events(this_week=True)

    syntax_slack = Notifier(config['slack']['token'])
    syntax_slack.notify_events(syntax_events)
