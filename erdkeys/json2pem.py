#!/usr/bin/env python3


import os
import os.path
import sys
from binascii import hexlify, unhexlify, b2a_base64
from json import load

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, hmac
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt


usage = 'json2pem.py json_file password'


if len(sys.argv) != 3:
    print('usage:', usage)
    sys.exit(1)
else:
    _, json_in, password = sys.argv
    json_path, json_filename = os.path.split(json_in)
    json_path = json_path or '.'


with open(json_in) as json_f:
    keystore = load(json_f)

backend = default_backend()


# derive the decryption key

kdf_name = keystore['crypto']['kdf']

if kdf_name != 'scrypt':
    print('unknown key derivation function', kdf_name)
    sys.exit(1)

salt = unhexlify(keystore['crypto']['kdfparams']['salt'])
n = keystore['crypto']['kdfparams']['n']
p = keystore['crypto']['kdfparams']['p']
r = keystore['crypto']['kdfparams']['r']

kdf = Scrypt(salt=salt, length=32, n=4096, r=8, p=1, backend=backend)
key = kdf.derive(bytes(password.encode()))


# decrypt the private key with half of the decryption key

cipher_name = keystore['crypto']['cipher']

if cipher_name != 'aes-128-ctr':
    print('unknown cipher or mode', cipher_name)
    sys.exit(1)

iv = unhexlify(keystore['crypto']['cipherparams']['iv'])
ciphertext = unhexlify(keystore['crypto']['ciphertext'])
decryption_key = key[0:16]

cipher = Cipher(algorithms.AES(decryption_key), modes.CTR(iv), backend=backend)
decryptor = cipher.decryptor()
plaintext = decryptor.update(ciphertext) + decryptor.finalize()
pemified_private_key = b2a_base64(hexlify(plaintext))


# verify the MAC, keyed with the other half of the encryption key
# (this is the only algorithm not explicitly declared but it outputs
# 256 bits and the most obviuos guess of SHA256 is also the right one)

hmac_key = key[16:32]
h = hmac.HMAC(hmac_key, hashes.SHA256(), backend=default_backend())
h.update(ciphertext)
mac = h.finalize()

if mac != unhexlify(keystore['crypto']['mac']):
    print('invalid keystore (MAC does not match)')
    sys.exit(1)


address_bech32 = keystore['bech32']
pem_out = '/'.join((json_path, address_bech32 + '.pem'))

with open(pem_out, 'w') as pem_f:
    pem_f.write('-----BEGIN PRIVATE KEY for %s-----\n' % address_bech32)
    pem_f.writelines('\n'.join([pemified_private_key[i:i+64].decode()
                                for i in range(0, len(pemified_private_key), 64)]))
    pem_f.write('-----END PRIVATE KEY for %s-----\n' % address_bech32)




 
