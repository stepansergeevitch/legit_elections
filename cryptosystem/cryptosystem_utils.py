# Utils used by cryptosystem modules.

from Crypto.Util import number
from random import randint

# Generate two random primes.
def generate_primes(bit_length):
    prime_p = generate_random_prime(bit_length)
    prime_q = generate_random_prime(bit_length)

    while prime_q == prime_p:
        prime_q = generate_random_prime(bit_length)

    return prime_p, prime_q


# Generates random prime with bit_length number of bits.
def generate_random_prime(bit_length):
    return number.getRandomNBitInteger(bit_length)


# Checks whether or not given integer is a prime.
# This probably should be a Miller-Rabin test if Python doesn't have a library.
def is_prime(p):
    if p < 2:
        return False

    i = 2
    while i * i <= p:
        if p % i == 0:
            return False
        i += 1

    return True


# Generates a coprime to a given integer.
def generate_coprime(n):
    r = randint(1, n - 1)
    while gcdex(r, n)[0] != 1:
        r = randint(1, n - 1)

    return r


# Calculates a to the power of b modulo mod.
def powmod(a, b, mod):
    a = (a + mod) % mod
    res = 1
    while b > 0:
        if b & 1:
            res = (res * a) % mod

        b = b >> 1
        a = (a * a) % mod

    return res


# Calculates the extended gcd.
def gcdex(a, b):
    assert a >= 0 and b >= 0

    if a == 0:
        return b, 0, 1

    g, x, y = gcdex(b % a, a)
    return g, y - (b // a) * x, x


# Calculates the inverse number to inv modulo mod.
def invmod(inv, mod):
    inv = (inv + mod) % mod
    g, x, y = gcdex(inv, mod)
    return (x + mod) % mod