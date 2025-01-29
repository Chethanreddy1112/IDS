import base64
import time
from datetime import datetime
from cryptography.fernet import Fernet
from hedera import Client, TopicMessageSubmitTransaction, TopicMessageQuery, Hbar, PrivateKey, TopicId

# Initialize Hedera client and keys
client = Client.for_testnet()
client.set_operator(PrivateKey.from_string("<Your Private Key>"), "<Your Account ID>")

# Generate key for encryption (can be saved for later use)
encryption_key = Fernet.generate_key()
cipher_suite = Fernet(encryption_key)

# Create a Hedera Consensus Topic
def create_topic():
    topic_create_tx = client.create_topic()
    topic_id = topic_create_tx.get_receipt().topic_id
    print(f"Topic Created: {topic_id}")
    return topic_id

# Encrypt the message before sending
def encrypt_message(message):
    encrypted_message = cipher_suite.encrypt(message.encode())
    return base64.b64encode(encrypted_message).decode()

# Decrypt the received message
def decrypt_message(encrypted_message):
    encrypted_message_bytes = base64.b64decode(encrypted_message.encode())
    decrypted_message = cipher_suite.decrypt(encrypted_message_bytes).decode()
    return decrypted_message

# Send a message to the topic
def send_message(topic_id, message):
    encrypted_message = encrypt_message(message)
    transaction = TopicMessageSubmitTransaction(client)
    transaction.set_topic_id(topic_id).set_message(encrypted_message)
    response = transaction.execute()
    print(f"Message Sent: \"{message}\" at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Query messages from the topic
def receive_messages(topic_id):
    message_query = TopicMessageQuery(client)
    message_query.set_topic_id(topic_id)
    messages = message_query.execute()

    print("\nMessages Received:")
    for i, msg in enumerate(messages):
        decrypted_message = decrypt_message(msg.message)
        timestamp = datetime.utcfromtimestamp(msg.consensus_timestamp.seconds).strftime('%Y-%m-%d %H:%M:%S')
        print(f"{i+1}. \"{decrypted_message}\" at {timestamp}")

# Filter messages based on a keyword
def filter_messages(messages, keyword):
    filtered_messages = [msg for msg in messages if keyword.lower() in msg.lower()]
    return filtered_messages

# Main function
def main():
    # Step 1: Create Topic
    topic_id = create_topic()

    # Step 2: Send Messages
    messages_to_send = ["Hello, Hedera!", "Learning HCS", "Message 3"]
    for msg in messages_to_send:
        send_message(topic_id, msg)
        time.sleep(1)  # Simulate time delay for message sending

    # Step 3: Receive Messages
    messages_received = []
    receive_messages(topic_id)

    # Step 4: Message Filtering
    keyword = "Hedera"
    print("\nFiltered Messages:")
    filtered_messages = filter_messages(messages_received, keyword)
    for msg in filtered_messages:
        print(f"\"{msg}\"")

if __name__ == "__main__":
    main()
