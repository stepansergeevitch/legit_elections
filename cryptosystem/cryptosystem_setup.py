# Initializes the cryptosystem by generating the private and public keys.

import time
from cryptosystem.cryptosystem_utils import *

# Below is the list of constants that are common in cryptosystem.

# Prime number bit length.
BIT_LENGTH = 256


# Generates public and private keys for the host.
def generate_keys():
    start = time.clock()

    # Generate primes.
    prime_p, prime_q = generate_primes(BIT_LENGTH)

    # Calculate public key.
    public_n = prime_p * prime_q
    public_g = public_n + 1

    # Calculate private key.
    private_phi = (prime_p-1) * (prime_q-1)
    private_s = invmod(public_n, private_phi)

    end = time.clock()
    print(f"Time spent for key generation: {time.clock() - start}")

    return public_n, public_g, private_phi, private_s


