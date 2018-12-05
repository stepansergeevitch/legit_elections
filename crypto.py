# This file contains basic election cryptographic related setup.

from candidates import NUMBER_OF_CANDIDATES, NUMBER_OF_MARKS
from cryptosystem.encryption import *
from cryptosystem.decryption import *
from cryptosystem.cryptosystem_setup import *
from aggregator import *


class Crypto(object):

    # Constructor.
    def __init__(self):
        keys = generate_keys()
        self.public_key = keys[:2]
        self.private_key = keys[2:4]

        self.encryptor = Encryptor(self.public_key)
        self.decryptor = Decryptor(self.public_key, self.private_key)

        self.aggregator = Aggregator(self.encryptor, self.decryptor, NUMBER_OF_CANDIDATES, NUMBER_OF_MARKS)

    # Adds new matrix of votes.
    def process(self, data):
        data = [[int(it) for it in row.split(',')] for row in data.split('\n')]
        self.aggregator.add_vote(data)

    # Aggregates and returns the winner.
    def aggregate(self):
        return self.aggregator.aggregate()
