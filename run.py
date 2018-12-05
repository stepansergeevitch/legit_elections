from server import Server

if __name__ == "__main__":
    server = Server(max_seconds=100000)
    server.run()
    server.wait_until_done()

    print("Finished gathering votes")
    # Some computations
