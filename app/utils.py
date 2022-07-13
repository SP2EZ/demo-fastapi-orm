from passlib.context import CryptContext

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return (password_context.hash(password))

def verify_password(payload_password, stored_password):
    return (password_context.verify(payload_password, stored_password))