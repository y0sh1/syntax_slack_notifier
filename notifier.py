from slackclient import SlackClient
import urllib.request
from configparser import ConfigParser

class Notifier:

    slack_token = ""

    def __init__(self, slack_token):
        self.slack_token = slack_token

    def notify(self, message):
        slack = SlackClient(token=self.slack_token)
        slack.api_call(
            "chat.postMessage",
            username="Syntax Notification Bot",
            icon_emoji=":robot_face:",
            channel="#testing",
            text=message
        )

class Events:

    events_url = ""

    def __init__(self, events_url):
        self.events_url = events_url
        events = self.get_events()
        print(events.read())

    def get_events(self):
        return urllib.request.urlopen(self.events_url)


if __name__ == "__main__":
    config = ConfigParser()
    config.read('config.ini')
    print()
    syntax_events = Events(config['syntax']['calendar_url'])

    syntax_slack = Notifier(config['slack']['token'])
    syntax_slack.notify("piew piew :tada:")
