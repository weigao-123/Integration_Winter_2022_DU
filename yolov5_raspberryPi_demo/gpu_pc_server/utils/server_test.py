import socket


def main():
    server_socket = socket.socket()
    server_socket.bind(('192.168.0.182', 8000))
    server_socket.listen(0)

    # accept a single connection
    connection = server_socket.accept()[0]
    while True:
        recv_data = connection.recv(1024)
        print('The received dataset is: ', recv_data.decode('utf-8'))
        if recv_data:
            send_data = input('Please answer your client: ')
            connection.send(send_data.encode('utf-8'))
        else:
            break

    server_socket.close()

if __name__ == '__main__':
    main()
