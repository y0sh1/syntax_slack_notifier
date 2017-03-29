from slackclient import SlackClient
import urllib.request
from configparser import ConfigParser
from ics import Calendar
import arrow
import argparse


class Notifier:
    slack_token = ""
    username = "USERNAME NOT SET"
    channel = ""
    icon = ":sad:"

    def __init__(self, username, channel, icon, slack_token):
        self.slack_token = slack_token
        self.username = username
        self.channel = "#" + channel
        self.icon = icon

    def notify(self, messages, attachments=None):
        if attachments is None:
            attachments = []
        slack = SlackClient(token=self.slack_token)
        for message in messages:
            slack.api_call(
                "chat.postMessage",
                username=self.username,
                icon_emoji=self.icon,
                channel=self.channel,
                text=message,
                attachments=attachments
            )

    def notify_events(self, events, announcement=""):
        event_attachments = []
        for event in events:
            event_attachments.append({"title": event.name,
                                      "text": str(event.begin.format('DD-MM-YYYY @ HH:mm')) + ' Tot ' + str(
                                          event.end.format('DD-MM-YYYY @ HH:mm')) + '\nLocatie: ' + event.location,
                                      "color": "#57B5E8"})
        self.notify([announcement], event_attachments)


class Events:
    events_url = ""

    def __init__(self, events_url):
        self.events_url = events_url

    def get_events(self):
        calendar = Calendar(urllib.request.urlopen(self.events_url).read().decode('iso-8859-1'))
        return calendar.events

    def get_future_events(self, this_week=False):
        events = self.get_events()
        future_events = []
        current_time = arrow.utcnow()
        this_monday = current_time.replace(days=-(current_time.weekday()), hour=0, minute=0, second=0, microsecond=0)
        this_sunday = current_time.replace(days=+(6 - (current_time.weekday())), hour=23, minute=59, second=59,
                                           microsecond=0)
        for unique_event in events:
            if this_week and unique_event.begin >= this_monday and unique_event.end <= this_sunday:
                future_events.append(unique_event)
            elif unique_event.begin.datetime >= current_time and not this_week:
                future_events.append(unique_event)
        return future_events

    def get_next_event(self):
        events = self.get_future_events()
        last_event = None
        for unique_event in events:
            if not last_event:
                last_event = unique_event
            if unique_event.begin < last_event.begin:
                last_event = unique_event
        return [last_event]


if __name__ == "__main__":
    config = ConfigParser()
    config.read('config.ini')

    parser = argparse.ArgumentParser()
    parser.add_argument("--week", help="Notify week summary of events of this week", action="store_true")
    parser.add_argument("--next", help="Notify next event", action="store_true")
    parser.add_argument("--all", help="Notify all upcoming events", action="store_true")
    args = parser.parse_args()

    syntax_events_this_week = Events(config['syntax']['calendar_url']).get_future_events(this_week=True)
    syntax_events = Events(config['syntax']['calendar_url']).get_future_events()
    syntax_next_event = Events(config['syntax']['calendar_url']).get_next_event()

    syntax_slack = Notifier(config['slack']['username'], config['slack']['channel'], config['slack']['icon'],
                            config['slack']['token'])
    if args.all and syntax_events:
        syntax_slack.notify_events(syntax_events, announcement="Dit zijn alle aankomende events:")
    if args.week and syntax_events_this_week:
        syntax_slack.notify_events(syntax_events_this_week, announcement="Deze week zijn de volgende events:")
    if args.next and syntax_next_event:
        syntax_slack.notify_events(syntax_next_event, announcement="Dit is het volgende event:")
