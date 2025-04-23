import hmac
import hashlib
import struct
import os

"""

pbkdf2_hmac_sha256() is a PBKDF2 implementation using HMAC-SHA256
as the pseudorandom function.

Arguments:
1) password: The input password (as bytes)
2) salt: The salt value (as bytes)
3) iterations: Number of iterations 


"""
def pbkdf2_hmac_sha256(password: bytes, salt: bytes, iterations: int) -> bytes:
    
    # Precompute the HMAC key if password is longer than block size
    if len(password) > hashlib.sha256().block_size:
        password = hashlib.sha256(password).digest()
    
    # Pad the password if needed
    password = password + b'\x00' * (hashlib.sha256().block_size - len(password))
    
    # Inner and outer padded keys for HMAC
    iKP = bytes(x ^ 0x36 for x in password)
    oKP = bytes(x ^ 0x5c for x in password)
    
    # Single block needed for 32-byte output, since SHA-256 produces 32-byte (256-bit) hashes
    block_number = 1
    msg = salt + struct.pack('>I', block_number)
    
    # Initial iteration
    U = hmac.new(iKP, msg, hashlib.sha256).digest()
    U = hmac.new(oKP, U, hashlib.sha256).digest()
    result = U
    
    # Subsequent iterations
    for _ in range(1, iterations):
        U = hmac.new(iKP, U, hashlib.sha256).digest()
        U = hmac.new(oKP, U, hashlib.sha256).digest()
        result = bytes(x ^ y for x, y in zip(result, U))
    
    return result[:32]  # Explicitly return first 32 bytes

# Example usage
if __name__ == "__main__":
    # Convert strings to bytes
    password = "uPassword000".encode('utf-8')
    salt = os.urandom(16)  # Generate a 16-byte random salt
    
    # Derive a 32-byte (256-bit) key with 100,000 iterations
    derived_key = pbkdf2_hmac_sha256(password, salt, iterations=100000)

    # Standard Resutlt
    standard_key = pbkdf2_hmac_sha256(password, salt, iterations=100000)
    # hashlib.pbkdf2_hmac('sha256', password, salt, iterations=100000)

    print(f"Password: {password.decode('utf-8')}")
    print(f"Salt: {salt.hex()}")
    print(f"Derived key ({len(derived_key)} bytes): {derived_key.hex()}")
    print(f"Standard key: {standard_key.hex()}")