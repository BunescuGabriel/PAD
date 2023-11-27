import socket
import threading
import time

class BrokerServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.connections = {}
        self.topics = {}
        self.lock = threading.Lock()

    def start(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.host, self.port))
        server_socket.listen(5)
        print(f"Broker started on {self.host}:{self.port}")

        while True:
            client_socket, _ = server_socket.accept()
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
            client_thread.start()

    def handle_client(self, client_socket):
        try:
            while True:
                data = client_socket.recv(1024)
                if not data:
                    break

                message = data.decode('utf-8')
                self.process_message(message, client_socket)
        except:
            pass
        finally:
            self.remove_client(client_socket)
            client_socket.close()

    def process_message(self, message, client_socket):
        parts = message.split()
        if len(parts) < 2:
            return

        command = parts[0].upper()
        if command == 'SUBSCRIBE':
            topic = parts[1]
            self.subscribe(client_socket, topic)
            print(f"Subscriber connected for topic: {topic}")
            # Send stored messages to the new subscriber if there are any
            self.send_stored_messages(client_socket, topic)
        elif command == 'PUBLISH':
            if len(parts) < 3:
                return 
            topic = parts[1]
            content = ' '.join(parts[2:])
            self.publish(client_socket, topic, content)
            print(f"Message from publisher on topic {topic}: {content}")
            # Store the message for subscribers who may connect later

    def subscribe(self, subscriber_socket, topic):
        with self.lock:
            self.connections[subscriber_socket] = topic
            if topic not in self.topics:
                self.topics[topic] = []
            self.topics[topic].append(subscriber_socket)

    def publish(self, publisher_socket, topic, content):
        with self.lock:
            if topic in self.topics:
                for subscriber_socket in self.topics[topic]:
                    if subscriber_socket != publisher_socket:
                        try:
                            subscriber_socket.send(content.encode('utf-8'))
                        except:
                            pass
            # Store the message for future subscribers
            if topic not in self.topics:
                self.topics[topic] = []
            self.topics[topic].append(content)
    

    def send_stored_messages(self, subscriber_socket, topic):
        if topic in self.topics:
            for stored_message in self.topics[topic]:
                try:
                    subscriber_socket.send(stored_message.encode('utf-8'))
                except:
                    pass

    def remove_client(self, client_socket):
        with self.lock:
            if client_socket in self.connections:
                topic = self.connections[client_socket]
                del self.connections[client_socket]
                print(f"Subscriber disconnected for topic: {topic}")
                # Remove the client socket from the topic's subscribers
                if topic in self.topics:
                    self.topics[topic].remove(client_socket)

if __name__ == '__main__':
    host = 'localhost'
    port = 5001
    broker_server = BrokerServer(host, port)
    broker_server.start()