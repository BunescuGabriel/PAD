import socket
import time

class Subscriber:
    def __init__(self, broker_host, broker_port, topic):
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.topic = topic
        self.connected = False

    def subscribe(self):
        while True:
            try:
                if not self.connected:
                    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    client_socket.connect((self.broker_host, self.broker_port))
                    client_socket.send(f"SUBSCRIBE {self.topic}".encode('utf-8'))
                    self.connected = True
                    print("Connected to broker")

                while True:
                    data = client_socket.recv(1024)
                    if not data:
                        break

                    message = data.decode('utf-8')
                    print(message)
                    # print(f"Message receive: {message}")  # Afișați fiecare mesaj pe o linie nouă

            except ConnectionRefusedError:
                print("Broker is not available. Retrying in 5 seconds...")
                self.connected = False
                time.sleep(5)
            except ConnectionResetError:
                print("Connection to the broker was forcibly closed. Retrying in 5 seconds...")
                self.connected = False
                time.sleep(5)
            except KeyboardInterrupt:
                break
            finally:
                client_socket.close()
                print("Disconnected from broker")

if __name__ == '__main__':
    broker_host = 'localhost'
    broker_port = 5001
    topic = input("Enter the topic to subscribe to: ").lower()
    subscriber = Subscriber(broker_host, broker_port, topic)
    subscriber.subscribe()
