import re
import logging
from time import sleep

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class Command(object):
    registry = dict()

    def __init__(self, fn):
        self.registry[fn.__name__] = {
            'cmd': fn,
            'argnames': fn.__code__.co_varnames,
            'help': fn.__doc__
        }
        self._fn = fn

    def __call__(self, *args, **kwargs):
        self._fn(*args, **kwargs)


class Slackish(object):
    message_queue = []
    default_message = "Command Executed!"
    default_error_message = "Something went wrong!"

    def __init__(self, slack_client, registry, **kwargs):
        # instantiate Slack
        self.slack_client = slack_client(kwargs.get('SLACK_BOT_TOKEN'))
        self.RTM_READ_DELAY = kwargs.get('RTM_READ_DELAY', 1)
        self.MENTION_REGEX = kwargs.get('MENTION_REGEX', "^<@(|[WU].+?)>(.*)")
        self.BOT_ID = kwargs.get('BOT_ID')
        self.registry = registry

    @classmethod
    def send(cls, message):
        """enqueue message in Slackish print queue"""
        cls.message_queue.append(message)

    def parse_bot_commands(self, slack_events):
        """
            Parses a list of events coming from the Slack RTM API to find bot commands.
            If a bot command is found, this function returns a tuple of command and channel.
            If its not found, then this function returns None, None.
        """
        for event in slack_events:
            if event["type"] == "message" and not "subtype" in event:
                user_id, message = self.parse_direct_mention(event["text"])
                if user_id == self.BOT_ID:
                    return message, event["channel"]
        return None, None

    def parse_direct_mention(self, message_text):
        """
            Finds a direct mention (a mention that is at the beginning) in message text
            and returns the user ID which was mentioned. If there is no direct mention, returns None
        """
        matches = re.search(self.MENTION_REGEX, message_text)
        # the first group contains the username, the second group contains the remaining message
        return (matches.group(1),
                matches.group(2).strip()) if matches else (None, None)

    def auth(self):
        """set BOT_ID (bot user_id) using auth.test api"""
        self.BOT_ID = self.slack_client.api_call("auth.test")["user_id"]

    def serve(self, registry=None):
        if registry:
            self.registry = registry
        if self.slack_client.rtm_connect(with_team_state=False):
            logger.info("Slackish Bot connected and authenticating!")
            self.auth()
            while True:
                logger.info("BOT serving loop started")
                command, channel = self.parse_bot_commands(
                    self.slack_client.rtm_read())
                self.channel = channel
                logger.info("BOT received {} from channel: {}".format(
                    command, channel))
                if command:
                    logger.info("handeling command: {}".format(command))
                    self.handle(command, channel, registry=self.registry)
                else:
                    logger.info("No commands passed!")
                sleep(self.RTM_READ_DELAY)
        else:
            logger.exception("Error while serving!")

    def detect_quoted_args(self, command):
        logger.info("Detecting quoted args!!")
        placeholders = {}
        delta = 0
        regex = regex = r"\"[\w\s,.-;()]*\""
        matches = re.finditer(regex, command, re.MULTILINE)
        for match_num, match in enumerate(matches):
            match_num = match_num + 1
            placeholder = "sub{num}".format(num=match_num)
            placeholders[placeholder.strip()] = match.group()[1:-1]
            start_index = match.start()
            end_index = match.end()
            new_command = command[:start_index -
                                  delta] + placeholder + command[end_index -
                                                                 delta:]
            delta = len(command) - len(new_command)
            command = new_command
        logger.info("detected: {}\n New command is:{}".format(placeholders, command))
        return command, placeholders

    def command_to_fn_call(self, command, registry):
        logger.debug("converting command to function call!")
        command, placeholders = self.detect_quoted_args(command)
        command_words = command.split()
        command_key = command_words[0].lower()
        logger.debug("command key is {}".format(command_key))
        try:
            cmd_function = registry[command_key]['cmd']
            logger.info('Executing command {}!'.format(command_key))
            kwargs = {}
            for i, v in enumerate(command_words):
                if i % 2:
                    logger.debug(v.lower() + ": " + command_words[i + 1])
                    kwargs[v.lower()] = placeholders.get(
                        command_words[i + 1], command_words[i + 1])
            cmd_function(**kwargs)
        except KeyError as KE:
            logger.debug("Command Key {} not found".format(command_key))
            logger.debug("Registery: " + registry)
            logger.exception(KE)

    def post(self, message):
        self.slack_client.api_call(
            "chat.postMessage",
            channel=self.channel,
            text=message or self.default_message)

    def error(self, error_message):
        self.slack_client.api_call(
            "chat.postMessage",
            channel=self.channel,
            text="Error: " + (error_message or self.default_error_message))

    def flush(self, message_queue):
        for message in message_queue:
            self.post(message)

    def handle(self, command, channel, registry):
        try:
            self.command_to_fn_call(command, registry)
            self.flush(Slackish.message_queue)
            Slackish.message_queue = []
        except Exception as e:
            logger.exception(e)
            self.flush(Slackish.message_queue)
            Slackish.message_queue = []
            self.error(self.default_error_message)
