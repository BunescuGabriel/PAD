import grpc
import publisher_pb2
import publisher_pb2_grpc

def send_message():
    channel = grpc.insecure_channel('localhost:5001')
    stub = publisher_pb2_grpc.PublisherStub(channel)

    while True:
        topic = input("Enter the topic: ").lower()
        content = input("Enter content: ")

        request = publisher_pb2.PublisherRequest(topic=topic, content=content)

        try:
            response = stub.PublishMessage(request)
            print(f"Publish Reply: {response.isSuccess}")
        except grpc.RpcError as e:
            print(f"Error publishing the message: {e.details()}")

if __name__ == '__main__':
    send_message()
