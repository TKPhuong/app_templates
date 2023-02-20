import sys
sys.path.append(r"C:\Users\N533\Local_IPS\Documents\Python\重点施策\app_template\src")
from templates.utils.log_tools.logger import log_init_master

# Initialize the logging system with custom parameters
logger = log_init_master(level="info", format='%(asctime)s %(levelname)s: %(message)s',
                         file_path='myapp.log', backup_count=7)


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