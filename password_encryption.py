from cryptography.fernet import Fernet

# Function to generate a key and save it into a file
def generate_key():
    key = Fernet.generate_key()
    with open("secret.key", "wb") as key_file:
        key_file.write(key)

# Function to load the key from the current directory named `secret.key`
def load_key():
    return open("secret.key", "rb").read()

# Function to encrypt a message
def encrypt_message(key,message):

    encoded_message = message.encode()
    f = Fernet(key)
    encrypted_message = f.encrypt(encoded_message)
    return encrypted_message

# Function to decrypt an encrypted message
def decrypt_message(encrypted_message):
    key = load_key()
    f = Fernet(key)
    decrypted_message = f.decrypt(encrypted_message)
    return decrypted_message.decode()

# Example usage
if __name__ == "__main__":
    generate_key()  # Generate a key and save it for the first time

    # Encrypt a password
    password = "my_super_secret_password"
    encrypted_password = encrypt_message(password)
    print(f"Encrypted: {encrypted_password}")

    # Decrypt the password
    decrypted_password = decrypt_message(encrypted_password)
    print(f"Decrypted: {decrypted_password}")
