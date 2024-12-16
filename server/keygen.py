import pickle
import uuid
from Crypto.Random import get_random_bytes
key = get_random_bytes(16)
with open(f"key-{str(uuid.uuid4())[:8]}", "wb") as f:
    f.write(key)