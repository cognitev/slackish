Slackish
========
Slackish is small library that lets you convert you simple functions into running slack bots.


Usage
-----
```python
from slack_client import SlackClient
from slackish import Slackish, Command

@Command
def create(campaign,on='Bing')
    #Do some logic here!
    Slackish.send("Campaign created succesfully!)

config = {}
config['BOT_ID'] = None
config['RTM_READ_DELAY'] = 1
config['SLACK_BOT_TOKEN'] = 'SOME TOKEN HERE'
config['SLACK_MENTION_REGEX] = "^<@(|[WU].+?)>(.*)"
my_bot = Slackish(SlackClient, **config)
my_bot.serve(Command.registry)
```