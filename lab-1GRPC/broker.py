import grpc
import subscriber_pb2
import subscriber_pb2_grpc
import publisher_pb2
import publisher_pb2_grpc
import notifier_pb2
import notifier_pb2_grpc
from concurrent import futures
import time
import threading

class Connection:
    def __init__(self, address, topic):
        self.address = address
        self.topic = topic
        self.channel = grpc.insecure_channel(address)

class ConnectionStorage:
    def __init__(self):
        self.connections = []
        self.lock = threading.Lock()

    def add(self, connection):
        with self.lock:
            self.connections.append(connection)

    def remove(self, address):
        with self.lock:
            self.connections = [conn for conn in self.connections if conn.address != address]

    def get_connections_by_topic(self, topic):
        with self.lock:
            return [conn for conn in self.connections if conn.topic == topic]

class Message:
    def __init__(self, topic, content):
        self.topic = topic
        self.content = content

class MessageStorage:
    def __init__(self):
        self.messages = {}
        self.lock = threading.Lock()

    def add(self, message):
        with self.lock:
            topic = message.topic
            if topic not in self.messages:
                self.messages[topic] = []
            self.messages[topic].append(message)

    def get_messages_by_topic(self, topic):
        with self.lock:
            return self.messages.get(topic, [])

    def remove_messages_by_topic(self, topic):
        with self.lock:
            if topic in self.messages:
                del self.messages[topic]

    def is_empty(self):
        with self.lock:
            return not bool(self.messages)

class PublisherService(publisher_pb2_grpc.PublisherServicer):
    def __init__(self, message_storage):
        self.message_storage = message_storage

    def PublishMessage(self, request, context):
        print(f"Received: {request.topic} {request.content}")
        message = Message(request.topic, request.content)
        self.message_storage.add(message)
        return publisher_pb2.PublisherReply(isSuccess=True)

class SubscriberService(subscriber_pb2_grpc.SubscriberServicer):
    def __init__(self, connection_storage):
        self.connection_storage = connection_storage

    def Subscribe(self, request, context):
        print(f"New client trying to subscribe: {request.address} {request.topic}")
        try:
            connection = Connection(request.address, request.topic)
            self.connection_storage.add(connection)
            print(f"New client subscribed: {request.address} {request.topic}")
            # Trimit mesajele stocate pentru acest topic către noul abonat
            message_storage = MessageStorage()
            messages = message_storage.get_messages_by_topic(request.topic)
            connections = self.connection_storage.get_connections_by_topic(request.topic)
            for connection in connections:
                try:
                    stub = notifier_pb2_grpc.NotifierStub(connection.channel)
                    for message in messages:
                        response = stub.Notify(notifier_pb2.NotifyRequest(content=message.content))
                        print(f"Notified new subscriber {connection.address} with {message.content}. Response: {response.isSuccess}")
                except grpc.RpcError as e:
                    if e.code() == grpc.StatusCode.UNAVAILABLE:
                        # Clientul nu este disponibil, eliminăm-l din lista de conexiuni
                        removed_conn = self.connection_storage.remove(connection.address)
                        if removed_conn:
                            print(f"Client disconnected: {removed_conn.address}")
                    else:
                        print(f"RPC Error notifying subscriber {connection.address}. {e.details()}")
                except Exception as e:
                    print(f"Error notifying subscriber {connection.address}. {str(e)}")
        except Exception as e:
            print(f"Could not add the new connection {request.address} {request.topic}. {str(e)}")
        return subscriber_pb2.SubscriberReply(isSuccess=True)


class SenderWorker:
    def __init__(self, message_storage, connection_storage):
        self.message_storage = message_storage
        self.connection_storage = connection_storage

    def start(self):
        while True:
            while not self.message_storage.is_empty():
                for topic, messages in list(self.message_storage.messages.items()):
                    connections = self.connection_storage.get_connections_by_topic(topic)
                    
                    for connection in connections:
                        try:
                            stub = notifier_pb2_grpc.NotifierStub(connection.channel)
                            for message in messages:
                                response = stub.Notify(notifier_pb2.NotifyRequest(content=message.content))
                                print(f"Notified subscriber {connection.address} with {message.content}. Response: {response.isSuccess}")
                            # După ce am trimis toate mesajele, eliminăm mesajele pentru acest topic
                            self.message_storage.remove_messages_by_topic(topic)
                        except grpc.RpcError as e:
                            if e.code() == grpc.StatusCode.UNAVAILABLE:
                                # Clientul nu este disponibil, eliminăm-l din lista de conexiuni
                                removed_conn = self.connection_storage.remove(connection.address)
                                if removed_conn:
                                    print(f"Client disconnected: {removed_conn.address}")
                            else:
                                print(f"RPC Error notifying subscriber {connection.address}. {e.details()}")
                        except Exception as e:
                            print(f"Error notifying subscriber {connection.address}. {str(e)}")


if __name__ == '__main__':
    connection_storage = ConnectionStorage()
    message_storage = MessageStorage()
    publisher_service = PublisherService(message_storage)
    subscriber_service = SubscriberService(connection_storage)
    sender_worker = SenderWorker(message_storage, connection_storage)

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    publisher_pb2_grpc.add_PublisherServicer_to_server(publisher_service, server)
    subscriber_pb2_grpc.add_SubscriberServicer_to_server(subscriber_service, server)
    server.add_insecure_port('[::]:5001')
    server.start()

    print("Broker started on port 5001")

    sender_thread = threading.Thread(target=sender_worker.start)
    sender_thread.start()

    try:
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        print("Received KeyboardInterrupt. Stopping server...")
        server.stop(0)
        sender_thread.join()  
        print("Server stopped.")
