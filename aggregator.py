# This is responsible for the aggregation of voting results.

import numpy as np

from candidates import *
from cryptosystem.encrypted_routine import *
from cryptosystem.cryptosystem_utils import *
from cryptosystem.cryptosystem_setup import *
from cryptosystem.encryption import *
from cryptosystem.decryption import *


class Aggregator(object):

    # Constructor.
    def __init__(self, encryptor, decryptor, rows, cols):
        self.encryptor = encryptor
        self.decryptor = decryptor

        self.matrix = np.array([encryptor.encrypt(0) for i in range(rows * cols)]).reshape(rows, cols)

    # Add votes to current matrix.
    def add_vote(self, data):
        modulo = self.encryptor.public_key[0] * self.encryptor.public_key[0]

        data = np.array(data)
        n, m = self.matrix.shape
        assert (n, m) == data.shape

        for i in range(0, n):
            for j in range(0, m):

                x, y = prepare_different_arrays(
                    bit_extraction_gate(self.matrix[i, j], self.encryptor, self.decryptor),
                    convert_to_bit_array(self.decryptor.decrypt(data[i, j])),
                    self.encryptor
                )
                self.matrix[i, j] = to_number(
                    addition_gate(x, y, self.encryptor, self.decryptor), modulo, self.encryptor, self.decryptor)

    # Aggregate the votes.
    def aggregate(self):
        n, m = self.matrix.shape
        c = np.zeros((n, m))
        g = np.zeros(m)

        # Create matrix c.
        for i in range(n):
            for j in range(0, m):
                left = self.add_array(self.matrix[i, 0:j], self.matrix[i, 0:j])
                right = self.add_array(self.matrix[i, j + 1:m])

                left = bit_extraction_gate(left, self.encryptor, self.decryptor)
                right = bit_extraction_gate(right, self.encryptor, self.decryptor)

                left, right = prepare_similar_arrays(left, right, self.encryptor)
                c[i, j] = greater_than_gate(right, left, self.encryptor)

        # Create vector g.
        index_of_first_zero = -1

        for j in range(0, m):
            encrypted_res = self.encryptor.encrypt(1)
            for i in range(0, n):
                encrypted_res = conditional_gate(encrypted_res, c[i, j], self.decryptor)

            g[j] = encrypted_res
            if index_of_first_zero == -1 and self.decryptor.decrypt(g[j]) == 0:
                index_of_first_zero = j

        t = np.zeros((n, 2))
        for i in range(0, n):
            t[i, 0] = self.aggr(self.matrix[i], g, rev=False)
            t[i, 1] = self.aggr(self.matrix, g, rev=True)

        winner = 0
        for i in range(1, n):
            winner = self.compare(winner, i, c, t)

        return winner

    # Adds encrypted array.
    def add_array(self, x, y=[]):
        modulo = self.encryptor.public_key[0] * self.encryptor.public_key[0]
        encrypted_result = self.encryptor.encrypt(0)

        for i in range(0, len(x)):
            left, right = prepare_different_arrays(
                bit_extraction_gate(encrypted_result, self.encryptor, self.decryptor),
                convert_to_bit_array(self.decryptor.decrypt(x[i])),
                self.encryptor
            )

            encrypted_result = to_number(
                addition_gate(left, right, self.encryptor, self.decryptor), modulo, self.encryptor, self.decryptor)

        if len(y) > 0:
            for i in range(0, len(y)):
                left, right = prepare_different_arrays(
                    bit_extraction_gate(encrypted_result, self.encryptor, self.decryptor),
                    convert_to_bit_array(self.decryptor.decrypt(y[i])),
                    self.encryptor
                )

                encrypted_result = to_number(
                    addition_gate(left, right, self.encryptor, self.decryptor), modulo, self.encryptor, self.decryptor)

        return encrypted_result

    def aggr(self, x, g, rev=False):
        modulo = self.encryptor.public_key[0] * self.encryptor.public_key[0]

        encrypted_result = self.encryptor.encrypt(0)

        if not rev:
            for i in range(0, len(x)):
                cur_result = conditional_gate(x[i], g[i], self.decryptor)
                left, right = prepare_different_arrays(
                    bit_extraction_gate(encrypted_result, self.encryptor, self.decryptor),
                    convert_to_bit_array(self.decryptor.decrypt(cur_result)),
                    self.encryptor
                )

                encrypted_result = to_number(
                    addition_gate(left, right, self.encryptor, self.decryptor), modulo, self.encryptor, self.decryptor)
        else:
            for i in range(1, len(x)):
                cur_result = (self.encryptor.encrypt(1) * invmod(g[i - 1], modulo)) % modulo
                left, right = prepare_different_arrays(
                    bit_extraction_gate(encrypted_result, self.encryptor, self.decryptor),
                    convert_to_bit_array(self.decryptor.decrypt(cur_result)),
                    self.encryptor
                )

                encrypted_result = to_number(
                    addition_gate(left, right, self.encryptor, self.decryptor), modulo, self.encryptor, self.decryptor)

        return encrypted_result

    def compare(self, winner, potential, c, t):
        index_w = self.get_index(winner, c)
        index_p = self.get_index(potential, c)

        if index_w < index_p:
            return winner
        elif index_p < index_w:
            return potential
        else:
            bitwise_w_one = bit_extraction_gate(t[winner, 0], self.encryptor, self.decryptor)
            bitwise_w_two = bit_extraction_gate(t[winner, 1], self.encryptor, self.decryptor)

            bitwise_p_one = bit_extraction_gate(t[potential, 0], self.encryptor, self.decryptor)
            bitwise_p_two = bit_extraction_gate(t[potential, 1], self.encryptor, self.decryptor)

            if self.better2(bitwise_w_one, bitwise_w_two, bitwise_p_one, bitwise_p_two):
                return winner
            elif self.better2(bitwise_p_one, bitwise_p_two, bitwise_w_one, bitwise_w_two):
                return potential
            else:
                if self.better3(bitwise_w_one, bitwise_w_two, bitwise_p_one, bitwise_p_two):
                    return winner
                elif self.better3(bitwise_p_one, bitwise_p_two, bitwise_w_one, bitwise_w_two):
                    return potential
                else:
                    if self.better4(bitwise_p_one, bitwise_p_two, bitwise_w_one, bitwise_w_two):
                        return potential
                    else:
                        return winner

    def better2(self, bitwise_x_one, bitwise_x_two, bitwise_y_one, bitwise_y_two):
        first = self.decryptor.decrypt(greater_than_gate(bitwise_x_one, bitwise_x_two, self.encryptor, self.decryptor)) == 1
        second = self.decryptor.decrypt(greater_than_gate(bitwise_y_two, bitwise_y_one, self.encryptor, self.decryptor)) == 1
        return first and second

    def better3(self, bitwise_x_one, bitwise_x_two, bitwise_y_one, bitwise_y_two):
        first = self.decryptor.decrypt(
            greater_than_gate(bitwise_x_one, bitwise_x_two, self.encryptor, self.decryptor)) == 1
        second = self.decryptor.decrypt(
            greater_than_gate(bitwise_y_one, bitwise_y_two, self.encryptor, self.decryptor)) == 1
        third = self.decryptor.decrypt(
            greater_than_gate(bitwise_x_one, bitwise_y_one, self.encryptor, self.decryptor)) == 1
        return first and second and third

    def better4(self, bitwise_x_one, bitwise_x_two, bitwise_y_one, bitwise_y_two):
        first = self.decryptor.decrypt(
            greater_than_gate(bitwise_x_two, bitwise_x_one, self.encryptor, self.decryptor)) == 1
        second = self.decryptor.decrypt(
            greater_than_gate(bitwise_y_two, bitwise_y_one, self.encryptor, self.decryptor)) == 1
        third = self.decryptor.decrypt(
            greater_than_gate(bitwise_y_two, bitwise_x_two, self.encryptor, self.decryptor)) == 1
        return first and second and third

    def get_index(self, row, c):
        for i in range(0, len(row)):
            if self.decryptor.decrypt(c[row, i]) == 0:
                return i

        return len(row) - 1


keys = generate_keys()
enc = Encryptor(keys[0:2])
dec = Decryptor(keys[0:2], keys[2:4])
a = Aggregator(enc, dec, NUMBER_OF_CANDIDATES, NUMBER_OF_MARKS)
print(a.matrix)

test = [enc.encrypt(1) for i in range(NUMBER_OF_CANDIDATES * NUMBER_OF_MARKS)]
test = np.array(test).reshape(NUMBER_OF_CANDIDATES, NUMBER_OF_MARKS)
print(test)
