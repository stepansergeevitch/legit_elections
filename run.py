from server import Server
from candidates import candidates, NUMBER_OF_CANDIDATES

if __name__ == "__main__":
    server = Server(max_seconds=100000)
    server.run()
    server.wait_until_done()

    print("Finished gathering votes")
    # Some computations
    winner = server.crypto.aggregate()
    assert 0 <= winner < NUMBER_OF_CANDIDATES
    print(f'Election winner is: {candidates[winner]}')
