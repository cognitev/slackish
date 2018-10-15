import unittest
from unittest import TestCase
from slackish import Command
class TestSlackishCommand(TestCase):
    def test_command(self):
        @Command
        def foo(bar='baz'):
            """This is test documentation"""
            print("hello, world")
        registry = { 'foo':{
            'cmd': foo,
            'help': "This is test documentation",
            'argnames': ("bar",)
            }
        }
        self.assertEqual(Command.registry['foo']['help'], registry['foo']['help'])
        self.assertEqual(Command.registry['foo']['argnames'], registry['foo']['argnames'])
    
    # def test_cmd_to_function_call(self):
        
if __name__ == '__main__':
    unittest.main()