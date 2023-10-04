import socket
import time

class Publisher:
    def __init__(self, broker_host, broker_port):
        self.broker_host = broker_host
        self.broker_port = broker_port

    def publish(self):
        while True:
            try:
                client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client_socket.connect((self.broker_host, self.broker_port))

                while True:
                    topic = input("Enter the topic: ").lower()
                    content = input("Enter content: ")
                    message = f"PUBLISH {topic}\n{content}\n"  # Adăugați \n pentru a separa titlul și conținutul și pentru a indica sfârșitul mesajului

                    client_socket.send(message.encode('utf-8'))

            except ConnectionRefusedError:
                print("Broker is not available. Retrying in 5 seconds...")
                time.sleep(5)
            except ConnectionResetError:
                print("Connection to the broker was forcibly closed. Retrying in 5 seconds...")
                time.sleep(5)
            except KeyboardInterrupt:
                break
            finally:
                client_socket.close()

if __name__ == '__main__':
    broker_host = 'localhost'
    broker_port = 5001
    publisher = Publisher(broker_host, broker_port)
    publisher.publish()
