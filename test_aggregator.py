from aggregator import *

keys = generate_keys()
enc = Encryptor(keys[0:2])
dec = Decryptor(keys[0:2], keys[2:4])
a = Aggregator(enc, dec, NUMBER_OF_CANDIDATES, NUMBER_OF_MARKS)
n, m = a.matrix.shape

print('\nInitial matrix:')
for i in range(n):
    print(f'Row: {[dec.decrypt(a.matrix[i, j]) for j in range(m)]}')

print()

test = [
    [0, 1, 0, 0, 0],
    [0, 0, 0, 1, 0],
    [0, 0, 0, 1, 0],
    [1, 0, 0, 0, 0],
    [0, 0, 0, 0, 1],
]

test1 = [
    [0, 0, 0, 0, 1],
    [0, 0, 0, 1, 0],
    [0, 1, 0, 0, 0],
    [0, 0, 1, 0, 0],
    [1, 0, 0, 0, 0],
]

test2 = [
    [0, 0, 0, 1, 0],
    [0, 0, 1, 0, 0],
    [1, 0, 0, 0, 0],
    [0, 0, 1, 0, 0],
    [0, 1, 0, 0, 0],
]

test3 = [
    [0, 0, 0, 1, 0],
    [0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0],
    [0, 1, 0, 0, 0],
    [0, 0, 1, 0, 0],
]

test = [[enc.encrypt(x) for x in row] for row in test]
test = np.array(test)
print(f'Encrypted vote:\n{test}')
print('Decrypted vote:')
for i in range(n):
    print([dec.decrypt(test[i, j]) for j in range(m)])

print()

test1 = [[enc.encrypt(x) for x in row] for row in test1]
test1 = np.array(test1)
print(f'Encrypted vote:\n{test1}')
print('Decrypted vote:')
for i in range(n):
    print([dec.decrypt(test1[i, j]) for j in range(m)])

print()

test2 = [[enc.encrypt(x) for x in row] for row in test2]
test2 = np.array(test2)
print(f'Encrypted vote:\n{test2}')
print('Decrypted vote:')
for i in range(n):
    print([dec.decrypt(test2[i, j]) for j in range(m)])

print()

test3 = [[enc.encrypt(x) for x in row] for row in test3]
test3 = np.array(test3)
print(f'Encrypted vote:\n{test3}')
print('Decrypted vote:')
for i in range(n):
    print([dec.decrypt(test3[i, j]) for j in range(m)])

print()

a.add_vote(test)
print('Decrypted aggregated matrix after vote:')
for i in range(n):
    print([dec.decrypt(a.matrix[i, j]) for j in range(m)])

print()

a.add_vote(test)
print('Decrypted aggregated matrix after vote:')
for i in range(n):
    print([dec.decrypt(a.matrix[i, j]) for j in range(m)])

print()

a.add_vote(test1)
print('Decrypted aggregated matrix after vote:')
for i in range(n):
    print([dec.decrypt(a.matrix[i, j]) for j in range(m)])

print()

a.add_vote(test2)
print('Decrypted aggregated matrix after vote:')
for i in range(n):
    print([dec.decrypt(a.matrix[i, j]) for j in range(m)])

print()

a.add_vote(test3)
print('Decrypted aggregated matrix after vote:')
for i in range(n):
    print([dec.decrypt(a.matrix[i, j]) for j in range(m)])

print()

for i in range(n):
    print(f'In row {i} array sums are: {[dec.decrypt(a.array_sum(a.matrix[i, 0:j])) for j in range(m + 1)]}')

c = a.create_candidate_matrix(a.matrix)
print(f'Encrypted candidate matrix:\n{c}')

print('Candidate matrix decrypted values:')
for i in range(n):
    print([dec.decrypt(c[i, j]) for j in range(m)])

g = a.create_grade_vector(c)
print(f'Encrypted grade vector: {g}')

print(f'Decrypted grade vector: {[dec.decrypt(g[i]) for i in range(m)]}')

t = a.create_tiebreak_matrix(a.matrix, g)
print(f'Encrypted tiebreak matrix:\n{t}')

print('Decrypted tiebreak matrix:')
for i in range(n):
    print([dec.decrypt(val) for val in t[i]])

winner = a.aggregate()
print(winner, candidates[winner])

