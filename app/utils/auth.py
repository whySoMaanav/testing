import bcrypt
import secrets
import string

def generate_access_code(length=16):
    """Generate a secure random access code formatted like XXXX-XXXX-XXXX-XXXX"""
    alphabet = string.ascii_uppercase + string.digits
    raw = ''.join(secrets.choice(alphabet) for _ in range(length))
    return '-'.join(raw[i:i+4] for i in range(0, len(raw), 4))

def hash_access_code(code: str) -> str:
    """Hash the access code using bcrypt"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(code.encode('utf-8'), salt).decode('utf-8')

def verify_access_code(code: str, hashed_code: str) -> bool:
    """Verify an access code against a hash"""
    return bcrypt.checkpw(code.encode('utf-8'), hashed_code.encode('utf-8'))
