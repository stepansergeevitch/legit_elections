# Defines Decryptor that is used to decrypt a message.

import time
from cryptosystem.cryptosystem_utils import *


class Decryptor(object):

    # Public key is (n, g).
    public_key = []

    # Private key is (phi, s).
    private_key = []

    # Constructor.
    def __init__(self, pub_key, priv_key):
        if len(pub_key) != 2:
            raise Exception(f'Did not provide correct number of arguments for the public _key. Received {pub_key}')

        if len(priv_key) != 2:
            raise Exception(f'Did not provide correct number of arguments for the private key. Received {priv_key}')

        self.public_key = pub_key
        self.private_key = priv_key

    # Decrypts the message.
    def decrypt(self, encrypted_message):
        start = time.clock()

        # Modulo is n^2.
        modulo = self.public_key[0] * self.public_key[0]

        # Calculate (cipher ^ phi) % n^2.
        res = powmod(encrypted_message, self.private_key[0], modulo)

        # According to algorithm, n must divide (res - 1).
        if (res - 1) % self.public_key[0] != 0:
            raise Exception(f'Error in cryptosystem. Decryption failed with this value: {res}')

        res = (res - 1) // self.public_key[0]

        print(f'Time spent for message decryption {time.clock() - start}')

        # Return (res * s) % n.
        return (res * self.private_key[1]) % self.public_key[0]

