# This file contains routine for math operations with encrypted data.
# Following operations are implemented:
# 1. Conditional gate: Encrypted equivalent of x * y, where y = 0 or 1.
# 2. Addition gate: Encrypted equivalent pf x + y.
# 3. Bit extraction gate: Extracting encrypted bits from encrypted value x.
# 4. Greater than gate: comparing two encrypted values.

from cryptosystem.cryptosystem_utils import *


# Conditional gate.
def conditional_gate(encrypted_x, encrypted_y, decryptor):
    y = decryptor.decrypt(encrypted_y)
    assert y == 0 or y == 1

    return powmod(encrypted_x, y, decryptor.public_key[0] * decryptor.public_key[0])


# Addition gate. Returns encrypted z = x + y.
def addition_gate(bitwise_encrypted_x, bitwise_y, encryptor, decryptor):
    n = encryptor.public_key[0]
    modulo = n * n

    encrypted_carry = encryptor.encrypt(0)
    bitwise_encrypted_result = []

    for i in range(0, len(bitwise_encrypted_x)):
        encrypted_num = (bitwise_encrypted_x[i] * encryptor.encrypt(bitwise_y[i])) % modulo
        encrypted_den = powmod(bitwise_encrypted_x[i], (bitwise_y[i] + bitwise_y[i]) % modulo, modulo)
        encrypted_cur_bit = (encrypted_num * invmod(encrypted_den, modulo)) % modulo

        encrypted_num = (encrypted_cur_bit * encrypted_carry) % modulo
        encrypted_den = powmod(conditional_gate(encrypted_cur_bit, encrypted_carry, decryptor), 2, modulo)
        bitwise_encrypted_result.append((encrypted_num * invmod(encrypted_den, modulo)) % modulo)

        encrypted_num = (bitwise_encrypted_x[i] * encryptor.encrypt(bitwise_y[i]) * encrypted_carry) % modulo
        encrypted_den = invmod(bitwise_encrypted_result[i], modulo)
        encrypted_carry = powmod((encrypted_num * encrypted_den) % modulo, (n + 1) >> 1, modulo)

    if decryptor.decrypt(encrypted_carry) > 0:
        bitwise_encrypted_result.append(encrypted_carry)

    return bitwise_encrypted_result


# Bit extraction gate.
def bit_extraction_gate(encrypted_x, encryptor, decryptor):
    n = encryptor.public_key[0]
    modulo = n * n

    # Get random coprime to n.
    y = generate_coprime(n)
    y_array = convert_to_bit_array(y)
    encrypted_y = encryptor.encrypt(y)
    encrypted_y_array = [encryptor.encrypt(bit_y) for bit_y in y_array]

    encrypted_z = (encrypted_x * invmod(encrypted_y, modulo)) % modulo
    z = decryptor.decrypt(encrypted_z)

    encrypted_y_array, z_array = prepare_different_arrays(encrypted_y_array, convert_to_bit_array(z), encryptor)
    encrypted_x_array = addition_gate(encrypted_y_array, z_array, encryptor, decryptor)

    return cut(encrypted_x_array, n, encryptor, decryptor)


# Returns 1 if encrypted_x is greater than encrypted_y.
# Calculation is done using this formula: result = (1 - (x - y)^2) * t + x(y - 1).
def greater_than_gate(bitwise_encrypted_x, bitwise_encrypted_y, encryptor, decryptor):
    n = encryptor.public_key[0]
    modulo = n * n

    encrypted_result = encryptor.encrypt(0)

    for i in range(0, len(bitwise_encrypted_x)):
        encrypted_cur_bit = conditional_gate(bitwise_encrypted_x[i], bitwise_encrypted_y[i], decryptor)

        encrypted_num = (encryptor.encrypt(1) * powmod(encrypted_cur_bit, 2, modulo)) % modulo
        encrypted_den = (bitwise_encrypted_x[i] * bitwise_encrypted_y[i]) % modulo
        encrypted_a = (encrypted_num * invmod(encrypted_den, modulo)) % modulo

        encrypted_b = conditional_gate(encrypted_a, encrypted_result, decryptor)

        encrypted_rest = (encrypted_b * bitwise_encrypted_x[i]) % modulo
        encrypted_result = (encrypted_rest * invmod(encrypted_cur_bit, modulo)) % modulo

    return encrypted_result


# Converts integer to bit array starting from the least significant bit.
def convert_to_bit_array(x):
    return [int(x) for x in reversed("{0:b}".format(x))]


# Prepares arrays of different kinds for addition gate by adding trailing zeros to make them equally sized.
# First array is expected to be encrypted array.
def prepare_different_arrays(encrypted_x, y, encryptor):
    while len(encrypted_x) < len(y):
        encrypted_x.append(encryptor.encrypt(0))

    while len(encrypted_x) > len(y):
        y.append(0)

    return encrypted_x, y


# Prepares arrays of the same kind for addition gate by adding trailing zeros to make them equally sized.
# Both arrays are either encrypted or decrypted.
def prepare_similar_arrays(x, y, encryptor=None):
    while len(x) < len(y):
        x.append(encryptor.encrypt(0) if encryptor is not None else 0)

    while len(x) > len(y):
        y.append(encryptor.encrypt(0) if encryptor is not None else 0)

    return x, y


# Calculates new encrypted number modulo mod since value it represents may be larger than mod.
def to_number(encrypted_array, mod, encryptor, decryptor):
    result = 0
    for i in range(0, len(encrypted_array)):
        result = (result + decryptor.decrypt(encrypted_array[i]) * (1 << i)) % mod

    return encryptor.encrypt(result)


# Calculates new encrypted array modulo mod since value it represents may be larger than mod.
def cut(encrypted_array, mod, encryptor, decryptor):
    result = 0
    for i in range(0, len(encrypted_array)):
        result = (result + decryptor.decrypt(encrypted_array[i]) * (1 << i)) % mod

    return [encryptor.encrypt(bit) for bit in convert_to_bit_array(result)]

