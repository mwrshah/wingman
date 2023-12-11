from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

# Function to load a public key from a file
def load_public_key(file_path):
    with open(file_path, "rb") as key_file:
        public_key = serialization.load_pem_public_key(
            key_file.read(),
            backend=default_backend()
        )
    return public_key

# Function to encrypt message
def encrypt_message(message, public_key):
    encrypted = public_key.encrypt(
        message.encode(),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return encrypted

# Example usage
public_key_file = "path/to/public_key.pem"  # Replace with your public key file path
public_key = load_public_key(public_key_file)
message = "This is a secret message"
encrypted_message = encrypt_message(message, public_key)
print("Encrypted:", encrypted_message)

