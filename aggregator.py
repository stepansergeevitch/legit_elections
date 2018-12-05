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

        self.matrix = np.array([encryptor.encrypt(0) for i in range(rows * cols)], dtype=object).reshape(rows, cols)

    # Add votes to current matrix.
    def add_vote(self, data):
        modulo = self.encryptor.public_key[0] * self.encryptor.public_key[0]

        data = np.array(data, dtype=object)
        n, m = self.matrix.shape
        assert (n, m) == data.shape

        for i in range(n):
            for j in range(m):
                x, y = prepare_different_arrays(
                    bit_extraction_gate(self.matrix[i, j], self.encryptor, self.decryptor),
                    convert_to_bit_array(self.decryptor.decrypt(data[i, j])),
                    self.encryptor
                )
                self.matrix[i, j] = to_number(
                    addition_gate(x, y, self.encryptor, self.decryptor), modulo, self.encryptor, self.decryptor)

    # Aggregate the votes.
    def aggregate(self):
        start = time.clock()

        n, m = self.matrix.shape

        # Create candidate matrix.
        c = self.create_candidate_matrix(self.matrix)

        print(f'All up to candidate matrix creation took: {time.clock() - start}')

        # Create grade vector.
        g = self.create_grade_vector(c)

        print(f'All up to grade vector creation took: {time.clock() - start}')

        # Create tiebreak matrix.
        t = self.create_tiebreak_matrix(self.matrix, g)

        print(f'All up to tiebreak matrix creation took: {time.clock() - start}')

        winner = 0
        for i in range(1, n):
            winner = self.get_better_candidate(winner, i, c, t)

        print(f'Full aggregation took: {time.clock() - start}')

        return winner

    # Creates candidate matrix.
    def create_candidate_matrix(self, aggregated_matrix):
        n, m = aggregated_matrix.shape
        c = np.zeros((n, m), dtype=object)

        for i in range(n):
            row_total = self.array_sum(aggregated_matrix[i, 0:(m + 1)])
            bitwise_row_total = bit_extraction_gate(row_total, self.encryptor, self.decryptor)

            for j in range(m):
                left = self.array_sum(aggregated_matrix[i, 0:j], aggregated_matrix[i, 0:j])
                bitwise_left = bit_extraction_gate(left, self.encryptor, self.decryptor)

                left, total = prepare_similar_arrays(bitwise_left, bitwise_row_total, self.encryptor)
                c[i, j] = greater_than_gate(total, left, self.encryptor, self.decryptor)

        return c

    # Creates grade vector.
    def create_grade_vector(self, candidate_matrix):
        n, m = candidate_matrix.shape
        g = np.zeros(m, dtype=object)

        for j in range(m):
            encrypted_res = self.encryptor.encrypt(1)
            for i in range(n):
                encrypted_res = conditional_gate(encrypted_res, candidate_matrix[i, j], self.decryptor)

            g[j] = encrypted_res

        return g

    # Creates tiebreak matrix.
    def create_tiebreak_matrix(self, aggregated_matrix, grade_vector):
        n, m = aggregated_matrix.shape
        t = np.zeros((n, 2), dtype=object)

        for i in range(0, n):
            t[i, 0] = self.linear_combination(self.matrix[i], grade_vector, reverse=False)
            t[i, 1] = self.linear_combination(self.matrix[i], grade_vector, reverse=True)

        return t

    # Adds encrypted array.
    def array_sum(self, x, y=[]):
        modulo = self.encryptor.public_key[0] * self.encryptor.public_key[0]
        encrypted_result = self.encryptor.encrypt(0)

        for xi in x:
            encrypted_result = self.add_encrypted(encrypted_result, xi, modulo)

        if len(y) > 0:
            for yi in y:
                encrypted_result = self.add_encrypted(encrypted_result, yi, modulo)

        return encrypted_result

    # Computes sum(x[i] * g[i]) or sum(x[n - i] * g[i]) depending on the reverse parameter.
    def linear_combination(self, x, g, reverse=False):
        modulo = self.encryptor.public_key[0] * self.encryptor.public_key[0]

        encrypted_result = self.encryptor.encrypt(0)

        if not reverse:
            for i in range(len(x)):
                cur_result = conditional_gate(x[i], g[i], self.decryptor)
                encrypted_result = self.add_encrypted(encrypted_result, cur_result, modulo)

        else:
            for i in range(1, len(x)):
                cur_result = (self.encryptor.encrypt(1) * invmod(g[i - 1], modulo)) % modulo
                cur_result = conditional_gate(x[i], cur_result, self.decryptor)

                encrypted_result = self.add_encrypted(encrypted_result, cur_result, modulo)

        return encrypted_result

    # Picks better candidate between the two. If all fields are equal picks first candidate.
    def get_better_candidate(self, winner, potential, candidate_matrix, t):
        index_w = self.get_first_zero_index(candidate_matrix[winner])
        index_p = self.get_first_zero_index(candidate_matrix[potential])

        if index_w < index_p:
            return winner
        elif index_p < index_w:
            return potential

        # Convert to bit representations.
        bitwise_w_one = bit_extraction_gate(t[winner, 0], self.encryptor, self.decryptor)
        bitwise_w_two = bit_extraction_gate(t[winner, 1], self.encryptor, self.decryptor)
        bitwise_p_one = bit_extraction_gate(t[potential, 0], self.encryptor, self.decryptor)
        bitwise_p_two = bit_extraction_gate(t[potential, 1], self.encryptor, self.decryptor)

        bitwise_w_one, bitwise_w_two = prepare_similar_arrays(bitwise_w_one, bitwise_w_two, self.encryptor)
        bitwise_p_one, bitwise_p_two = prepare_similar_arrays(bitwise_p_one, bitwise_p_two, self.encryptor)
        bitwise_w_one, bitwise_p_one = prepare_similar_arrays(bitwise_w_one, bitwise_p_one, self.encryptor)
        bitwise_w_two, bitwise_p_two = prepare_similar_arrays(bitwise_w_two, bitwise_p_two, self.encryptor)

        return self.additional_tests_winner(winner, potential,
                                            bitwise_w_one, bitwise_w_two,
                                            bitwise_p_one, bitwise_p_two)

    # Applies additional tests to determine winner between two candidates.
    def additional_tests_winner(self, x, y, bitwise_x_one, bitwise_x_two, bitwise_y_one, bitwise_y_two):
        # Apply second test.
        if self.better_second_test(bitwise_x_one, bitwise_x_two, bitwise_y_one, bitwise_y_two):
            return x
        elif self.better_second_test(bitwise_y_one, bitwise_y_two, bitwise_x_one, bitwise_x_two):
            return y

        # Apply third test if second test can't determine the winner.
        if self.better_third_test(bitwise_x_one, bitwise_x_two, bitwise_y_one, bitwise_y_two):
            return x
        elif self.better_third_test(bitwise_y_one, bitwise_y_two, bitwise_x_one, bitwise_x_two):
            return y

        # Apply fourth test if previous tests can't determine the winner.
        if self.better_fourth_test(bitwise_x_one, bitwise_x_two, bitwise_y_one, bitwise_y_two):
            return x
        elif self.better_fourth_test(bitwise_y_one, bitwise_y_two, bitwise_x_one, bitwise_x_two):
            return y

        # Candidates are equal. Return x.
        return x

    # Applies second test to determine better candidate between the two.
    def better_second_test(self, bitwise_x_one, bitwise_x_two, bitwise_y_one, bitwise_y_two):
        first = self.decryptor.decrypt(
            greater_than_gate(bitwise_x_one, bitwise_x_two, self.encryptor, self.decryptor)) == 1
        second = self.decryptor.decrypt(
            greater_than_gate(bitwise_y_one, bitwise_y_two, self.encryptor, self.decryptor)) == 0
        return first and second

    # Applies third test to determine better candidate between the two.
    def better_third_test(self, bitwise_x_one, bitwise_x_two, bitwise_y_one, bitwise_y_two):
        first = self.decryptor.decrypt(
            greater_than_gate(bitwise_x_one, bitwise_x_two, self.encryptor, self.decryptor)) == 1
        second = self.decryptor.decrypt(
            greater_than_gate(bitwise_y_one, bitwise_y_two, self.encryptor, self.decryptor)) == 1
        third = self.decryptor.decrypt(
            greater_than_gate(bitwise_x_one, bitwise_y_one, self.encryptor, self.decryptor)) == 1
        return first and second and third

    # Applies fourth test to determine better candidate between the two.
    def better_fourth_test(self, bitwise_x_one, bitwise_x_two, bitwise_y_one, bitwise_y_two):
        first = self.decryptor.decrypt(
            greater_than_gate(bitwise_x_one, bitwise_x_two, self.encryptor, self.decryptor)) == 0
        second = self.decryptor.decrypt(
            greater_than_gate(bitwise_y_one, bitwise_y_two, self.encryptor, self.decryptor)) == 0
        third = self.decryptor.decrypt(
            greater_than_gate(bitwise_y_two, bitwise_x_two, self.encryptor, self.decryptor)) == 1
        return first and second and third

    # Gets index of the first zero in a row of the matrix c.
    def get_first_zero_index(self, candidate_matrix_row):
        for i in range(len(candidate_matrix_row)):
            if self.decryptor.decrypt(candidate_matrix_row[i]) == 0:
                return i

        return len(candidate_matrix_row) - 1

    # Adds encrypted and unencrypted numbers.
    def add_encrypted(self, encrypted_x, unencrypted_y, modulo):
        left, right = prepare_different_arrays(
            bit_extraction_gate(encrypted_x, self.encryptor, self.decryptor),
            convert_to_bit_array(self.decryptor.decrypt(unencrypted_y)),
            self.encryptor
        )

        return to_number(
            addition_gate(left, right, self.encryptor, self.decryptor), modulo, self.encryptor, self.decryptor)
