import socket

from cryptosystem.encryption import Encryptor


class Client:
    KEY_REQUEST = b"KEY\n"
    DATA_REQUEST = b"DATA\n"
    NAMES_REQUEST = b"NAMES\n"
    SUCCESS = b"SUCCESS\n"
    ERROR = b"ERROR\n"

    def __init__(self, server_ip="127.0.0.1", server_port=9999):
        self.server_ip = server_ip
        self.server_port = server_port

        self.client = None
        self.pending_data_send = False

    def connect(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((self.server_ip, self.server_port))

    def close(self):
        self.client.close()
        self.client = None

    def request_names(self):
        self.connect()
        assert self.pending_data_send == False
        self.client.send(Client.NAMES_REQUEST)
        response = self.client.recv(1024)
        assert response.startswith(Client.NAMES_REQUEST)
        self.client.recv(1024)
        self.close()
        return response[len(Client.NAMES_REQUEST):].decode("utf-8").split("\n")

    def request_keys(self):
        self.connect()
        assert self.pending_data_send == False
        self.client.send(Client.KEY_REQUEST)
        response = self.client.recv(1024)
        assert response.startswith(Client.KEY_REQUEST)
        self.pending_data_send = True
        return [int(k) for k in response[len(Client.KEY_REQUEST):].decode("utf-8").split("\n")]

    def send_matrix(self, matrix):
        # Should have pending connection here
        assert self.pending_data_send == True

        data = '\n'.join(
            ','.join(row)
            for row in matrix
        ).encode("utf-8")

        self.client.send(Client.DATA_REQUEST + data)
        response = self.client.recv(1024)
        self.pending_data_send = False
        self.client.recv(1024)
        self.close()
        return response.startswith(self.SUCCESS)


def prompt_voting(names):
    print(f"For each candidate name please type you grade from 1 to {len(names)}")
    print("Each vote should be unique")
    votes = []
    valid = lambda v: v > 0 and v <= len(names)
    for name in names:
        vote = int(input(f"{name}: "))
        while vote in votes or not valid(vote):
            if vote in votes:
                print(f"You've already given this grade to {names[votes.index(vote)]}, please try again")
            else:
                print(f"Vote must be in between 1 and {len(vote)} inclusively")
            vote = int(input(f"{name}: "))
        votes.append(vote)
    return votes


def votes_to_matrix(votes):
    return [
        [1 if i + 1 == v else 0 for i in range(len(votes))]
        for v in votes
    ]


def encrypt_matrix(matrix, encryptor):
    return [
        [encryptor.encrypt(it) for it in row]
        for row in matrix
    ]


def run_votes():
    client = Client()
    names = client.request_names()
    votes = prompt_voting(names)
    keys = client.request_keys()
    matrix = votes_to_matrix(votes)
    encryptor = Encryptor(keys)
    enc_matrix = encrypt_matrix(matrix, encryptor)
    success = client.send_matrix(enc_matrix)
    if success:
        print("Your vote was sent successfully")
    else:
        print("There was error sending your vote")


if __name__ == "__main__":
    run_votes()


