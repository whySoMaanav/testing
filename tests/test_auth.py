import pytest
from app.utils.auth import generate_access_code, hash_access_code, verify_access_code

def test_generate_access_code():
    code = generate_access_code()
    assert len(code) == 19 # 16 chars + 3 dashes
    assert len(code.split('-')) == 4

def test_hash_and_verify_access_code():
    code = generate_access_code()
    hashed = hash_access_code(code)
    
    assert verify_access_code(code, hashed) is True
    assert verify_access_code("wrong-code", hashed) is False
