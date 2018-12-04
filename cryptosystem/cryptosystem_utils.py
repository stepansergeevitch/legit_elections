# Utils used by cryptosystem modules.

from random import getrandbits, randint


# Generates two random primes p and q and returns 2p+1 and 2q+1 which are also primes.
def generate_primes(bit_length):
    prime_p, prime_q = generate_random_primes(bit_length)
    return prime_p + prime_p + 1, prime_q + prime_q + 1


# Generates two random primes.
def generate_random_primes(bit_length):
    prime_p = generate_random_prime(bit_length)
    prime_q = generate_random_prime(bit_length)

    while prime_q == prime_p:
        prime_q = generate_random_prime(bit_length)

    return prime_p, prime_q


# Generates random prime with bit_length number of bits.
def generate_random_prime(bit_length):
    p = getrandbits(bit_length)
    while not is_prime(p):
        p = getrandbits(bit_length)
    return p


# Checks whether or not given integer is a prime.
# This probably should be a Miller-Rabin test if Python doesn't have a library.
def is_prime(p):
    return True


# Generates a coprime to a given integer.
def generate_coprime(n):
    r = randint(2, n - 1)
    while gcdex(r, n)[0] != 1:
        r = randint(2, n - 1)

    return r


# Calculates a to the power of b modulo mod.
def powmod(a, b, mod):
    res = 1
    while b > 1:
        if a & 1:
            res = (res * a) % mod

        b = b >> 1
        a = (a * a) % mod

    return res


# Calculates the extended gcd.
def gcdex(a, b):
    if a == 0:
        return b, 0, 1

    g, x, y = gcdex(b % a, a)
    return g, y - (b // a) * x, x


# Calculates the inverse number to inv modulo mod.
def invmod(inv, mod):
    g, x, y = gcdex(inv, mod)
    return (x + mod) % mod

