from server import Server

if __name__ == "__main__":
    server = Server(max_seconds=1000000)
    server.run()
    server.wait_until_done()

    print("Finished gathering votes")
    # Some computations
