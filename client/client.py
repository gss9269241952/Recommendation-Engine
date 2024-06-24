import socket

def send_request(request):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('localhost', 9998))
    client.send(request.encode())
    response = client.recv(4096)
    client.close()
    return response.decode()

if __name__ == "__main__":
    request = "ADMIN|ADD_MEAL|meal1|10|yes"
    # request = "ADMIN|CHANGE_PRICE||{new_price}"
    response = send_request(request)
    print("Client 1 Response:", response)
