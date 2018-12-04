# Defines Encryptor class that is used to encrypt messages.

import time
from cryptosystem.cryptosystem_utils import *


class Encryptor(object):

    # Public key is (n, g).
    public_key = []

    # Constructor.
    def __init__(self, pub_key):
        if len(pub_key) != 2:
            raise Exception(f'Did not provide correct number of arguments for the public _key. Received {pub_key}')

        self.public_key = pub_key

    # Encrypts the message.
    def encrypt(self, message):
        start = time.clock()

        # Modulo is n^2.
        modulo = self.public_key[0] * self.public_key[0]

        # First is (g^M) % n^2.
        first = powmod(self.public_key[1], message, modulo)

        # Second is (r^n) % n^2, where r is coprime to n.
        second = powmod(generate_coprime(self.public_key[0]), self.public_key[0], modulo)

        print(f'Time spent for message encryption {time.clock() - start}')

        return (first * second) % modulo
