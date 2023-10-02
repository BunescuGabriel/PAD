from concurrent import futures
import random
import grpc
import subscriber_pb2
import subscriber_pb2_grpc
import notifier_pb2_grpc
import notifier_pb2

DEFAULT_HOST = 'localhost'

class ReceiverService(notifier_pb2_grpc.NotifierServicer):
    def Notify(self, request, context):
        print(f"Receiver a primit notificarea: {request.content}")
        return notifier_pb2.NotifyReply(isSuccess=True)

def subscribe_to_topic(topic, address):
    channel = grpc.insecure_channel('localhost:5001')  # Adresa Broker-ului
    stub = subscriber_pb2_grpc.SubscriberStub(channel)

    request = subscriber_pb2.SubscriberRequest(topic=topic, address=address)

    try:
        response = stub.Subscribe(request)
        if response.isSuccess:
            print(f"Receiver s-a abonat cu succes la topicul '{topic}' pe adresa '{address}'")
        else:
            print(f"Abonarea la topicul '{topic}' a eșuat")
    except grpc.RpcError as e:
        print(f"Erroare la abonare: {e.details()}")

def start_receiver_server(address):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    notifier_pb2_grpc.add_NotifierServicer_to_server(ReceiverService(), server)
    server.add_insecure_port(address)  # Adresa la care ascultă Receiver-ul pentru notificări
    server.start()
    print(f"Receiver a pornit pe adresa {address} pentru notificări")
    try:
        while True:
            pass
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    # port = input("Introduceți adresa la care să ruleze receptorul (de exemplu,5002): ")
    port = random.randint(8000, 65535)
    address = f'{DEFAULT_HOST}:{port}'
    topic = input("Introduceți topicul la care doriți să vă abonați: ").lower()
    subscribe_to_topic(topic, address)
    start_receiver_server(address)
