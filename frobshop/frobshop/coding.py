

from cryptography.fernet import Fernet


def generate_key():
    return Fernet.generate_key()


def encrypt_card(key, card_number):
    cipher = Fernet(key)
    encrypted_message = cipher.encrypt(card_number.encode())
    return encrypted_message


def decrypt_card(key, encrypted_card_number):
    cipher = Fernet(key)
    decrypted_message = cipher.decrypt(encrypted_card_number)
    return decrypted_message.decode()

