# vapid_keygen.py generates a public and private keypair to use with Web-Pushies, see https://github.com/jazzband/django-push-notifications/blob/master/docs/WebPush.rst
# TODO: first install `pip install ecdsa`
# run with `py vapid_keygen.py`
import base64
import ecdsa

def generate_vapid_keypair():
    """
    Generate a new set of encoded key-pair for VAPID
    """
    pk = ecdsa.SigningKey.generate(curve=ecdsa.NIST256p)
    vk = pk.get_verifying_key()

    return {
        'private_key': base64.urlsafe_b64encode(pk.to_string()).strip(b"="),
        'public_key': base64.urlsafe_b64encode(b"\x04" + vk.to_string()).strip(b"=")
    }

print("\nStarting...\n")
keys = generate_vapid_keypair()

print("\nPrivate key (use for WP_PRIVATE_KEY setting):\n")
print(keys["private_key"].decode())
print("\nPublic key (use as Application Server Key in client JavaScript):\n")
print(keys["public_key"].decode())
print()