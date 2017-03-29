from slackclient import SlackClient
import urllib.request
from configparser import ConfigParser
from ics import Calendar
import arrow


class Notifier:
    slack_token = ""

    def __init__(self, slack_token):
        self.slack_token = slack_token

    def notify(self, messages, attachments=[]):
        slack = SlackClient(token=self.slack_token)
        for message in messages:
            slack.api_call(
                "chat.postMessage",
                username="Syntax Event Bot",
                icon_emoji=":calendar:",
                channel="#testing",
                text=message,
                attachments=attachments
            )

    def notify_events(self, events, announcement=""):
        event_attachments = []
        for event in events:
            event_attachments.append({"title": event.name,
                                      "text": str(event.begin.format('DD-MM-YYYY @ HH:mm')) + ' Tot ' + str(event.end.format('DD-MM-YYYY @ HH:mm')) + '\nLocatie: ' + event.location,
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
        events=self.get_future_events()
        last_event=None
        for unique_event in events:
            if not last_event:
                last_event = unique_event
            if unique_event.begin < last_event.begin:
                last_event = unique_event
        return [last_event]



if __name__ == "__main__":
    config = ConfigParser()
    config.read('config.ini')
    syntax_events_this_week = Events(config['syntax']['calendar_url']).get_future_events(this_week=True)
    syntax_events = Events(config['syntax']['calendar_url']).get_future_events()
    syntax_next_event = Events(config['syntax']['calendar_url']).get_next_event()

    syntax_slack = Notifier(config['slack']['token'])
    syntax_slack.notify_events(syntax_events, announcement="Dit zijn alle aankomende events:")
    syntax_slack.notify_events(syntax_events_this_week, announcement="Deze week zijn de volgende events:")
    syntax_slack.notify_events(syntax_next_event, announcement="Dit is het volgende event:")
