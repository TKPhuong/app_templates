import os
import sys
import shutil
import logging

# add the parent directory of the current file to the system path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from templates.utils.log_tools.logger import Logger
FILE_PATH = os.path.join(current_dir, 'log/myapp.log')

logger = Logger(level="info", 
                file_path=FILE_PATH,
                backup_count=7).get_logger()

class User:
    def __init__(self, name):
        self.name = name
        logger.info(f'User {name} created.')

    def send_message(self, message):
        logger.info(f'{self.name} sent message: {message}')
        chatroom.receive_message(self, message)

    def receive_message(self, message):
        logger.info(f'{self.name} received message: {message}')


class Chatroom:
    def __init__(self):
        self.users = []
        logger.info('Chatroom created.')

    def add_user(self, user):
        self.users.append(user)
        logger.info(f'User {user.name} added to chatroom.')

    def receive_message(self, sender, message):
        for user in self.users:
            if user != sender:
                logger.info(f'Chatroom received message from {sender.name}: {message}')
                user.receive_message(message)


if __name__ == '__main__':
    # Create some users and a chatroom
    alice = User('Alice')
    bob = User('Bob')
    chatroom = Chatroom()
    chatroom.add_user(alice)
    chatroom.add_user(bob)

    # Alice sends a message
    alice.send_message('Hi Bob!')

    # Bob sends a message
    bob.send_message('Hi Alice, how are you?')

    # Shut down logging system to remove the temporary log directory
    # logging.shutdown()

    # Clean up log file and directory
    # shutil.rmtree('./log')
