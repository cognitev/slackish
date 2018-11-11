Slackish
========
Slackish is small library that lets you convert your simple python functions into running slack bots.

sample_bot.py
-------------

```python
from slackclient import SlackClient
from slackish import Slackish, Command

@Command
def publish(campaign, on='rtx'):
    """Publish command for publishing campaigns
    *Usage*
    `publish campaign <campaign_id> on <traffic source>`
    """
    Slackish.send("I'll publish campaign {} on {}".format(campaign, on))

@Command
def standup(task, status):
    """Standup command for updating task status
    *Usage*
    `standup task <task_id> status <some status>`
    """
    Slackish.send("I'll update my status regarding task: {}".format(task))
    Slackish.send("Task is currently at status: {}".format(status))


config = {}
config['BOT_ID'] = None
config['RTM_READ_DELAY'] = 1
config['SLACK_BOT_TOKEN'] = 'SOME-TOKEN'
config['SLACK_MENTION_REGEX'] = "^(<@(|[WU].+?)>)?(.*)"
my_bot = Slackish(SlackClient, Command.registry, **config)
my_bot.serve()
```
<h2>Configure the token</h2>
<hr>
<h3> Open your slack channel 
<br>Select bots
</h3>
<img src="info/Selection_001.png">
<h3>Create your app</h3> 
<img src="info/Selection_002.png">

<h3>Get the access tokens and connect it to your code</h3> 
<img src="info/Selection_004.png">

```
config['SLACK_BOT_TOKEN'] = 'Add Your access API Token'
```
And run the bot
```
virtualenv .venv
source .venv/bin/activate
pip install -r requirements.txt
python sample_bot.py
```
Not sure what to tell your bot? Don't worry Slackish generate help messages based on the docstring!
<img src="info/Selection_005.png">


