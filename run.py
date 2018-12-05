from server import Server
from candidates import candidates, NUMBER_OF_CANDIDATES
import sys
import signal

def sigterm_handler(_bla, _te):
    server.stop()

server = Server(max_seconds=20)
signal.signal(signal.SIGTERM, sigterm_handler)
signal.signal(signal.SIGINT, sigterm_handler)

if __name__ == "__main__":
    server.run()
    server.wait_until_done()

    print("Finished gathering votes")
    # Some computations
    winner = server.crypto.aggregate()
    assert 0 <= winner < NUMBER_OF_CANDIDATES
    print(f'Election winner is: {candidates[winner]}')
