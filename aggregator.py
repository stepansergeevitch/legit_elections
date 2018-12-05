# This is responsible for the aggregation of voting results.

import numpy as np

from cryptosystem.encrypted_routine import *
from cryptosystem.cryptosystem_utils import *

class Aggregator(object):

    # Constructor.
    def __init__(self, encryptor, decryptor, rows, cols):
        self.encryptor = encryptor
        self.decryptor = decryptor

        self.matrix = np.array([encryptor.encrypt(0) for i in range(rows * cols)]).reshape(rows, cols)

    # Add votes to current matrix.
    def add_vote(self, data):
        n, m = self.matrix.shape()
        assert (n, m) == data.shape()

        for i in range(0, n):
            for j in range(0, m):
                self.matrix[i, j] = addition_gate(
                    self.matrix[i, j],
                    convert_to_bit_array(self.decryptor.decrypt(data[i, j])),
                    self.encryptor,
                    self.decryptor)

    # Aggregate the votes.
    def aggregate(self):
        pass



