#!/usr/bin/env python3


import os
import os.path
import re
import sys
from binascii import hexlify, unhexlify, a2b_hex, a2b_base64, Error
from json import dumps
from uuid import uuid4

from bech32 import convertbits, bech32_encode, bech32_decode
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, hmac
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt


usage = 'pem2json.py pem_file password'
password_pattern = '^(?=\S{9,}$)(?=.*?\d)(?=.*?[a-z])(?=.*?[A-Z])(?=.*?[^A-Za-z\s0-9])'


if len(sys.argv) != 3:
    print('usage:', usage)
    sys.exit(1)
else:
    _, pem_in, password = sys.argv
    pem_path, pe_filename = os.path.split(pem_in)
    pem_path = pem_path or '.'


address = ''
pvt_key = ''

with open(pem_in) as pem_f:
    
    for l in pem_f.readlines():
        
        if '-BEGIN PRIVATE KEY' in l:
            address = l.lstrip('-BEGIN PRIVATE KEY for ').rstrip('-\n')
        
        elif address and '-END PRIVATE KEY' in l:
            if not address == l.strip('-END PRIVATE KEY for ').rstrip('-\n'):
                print('invalid .pem file')
                sys.exit(1)
        
        else:
            pvt_key += l.strip('\n')


if not re.search(password_pattern, password):
    print('Your password must be at least 9 characters, an upper-case letter, a symbol & a number')
    sys.exit(1)


if not address and pvt_key:
    print('invalid .pem file')
    sys.exit(1)


#both hex and bech32 address format are needed for the json file

if address.startswith('erd1'):
    address_bech32 = address
    hrp, addr_5bits = bech32_decode(address)
    addr_8bits = convertbits(addr_5bits, 5, 8)[:-1] # why the extra 0 byte at the end?
    address_hex = ''.join([format(i, 'x') for i in addr_8bits])
else:
    address_hex = address
    addr_8bits = a2b_hex(address)
    addr_5bits = convertbits(addr_8bits, 8, 5)
    address_bech32 = bech32_encode('erd', addr_5bits)


try:
    pvt_key = unhexlify(a2b_base64(pvt_key)) #  funny!
except Error:
    print('invalid .pem file')
    sys.exit(1)


if not len(pvt_key) == 64:
    print('invalid .pem file')
    sys.exit(1)


backend = default_backend()


# derive the encryption key

salt = os.urandom(32)
kdf = Scrypt(salt=salt, length=32, n=4096, r=8, p=1, backend=backend)
key = kdf.derive(bytes(password.encode()))


# encrypt the private key with half of the encryption key

iv = os.urandom(16)
encryption_key = key[0:16]
cipher = Cipher(algorithms.AES(encryption_key), modes.CTR(iv), backend=backend)
encryptor = cipher.encryptor()
ciphertext = encryptor.update(pvt_key) + encryptor.finalize()


# compute the MAC, keyed with the other half of the encryption key
# (this is the only algorithm not explicitly declared but it outputs
# 256 bits and the most obviuos guess of SHA256 is also the right one)

hmac_key = key[16:32]
h = hmac.HMAC(hmac_key, hashes.SHA256(), backend=default_backend())
h.update(ciphertext)
mac = h.finalize()

uid = str(uuid4())

json = dumps({'version': 4, # what standard does it refer to?
              'id': uid,
              'address': address_hex,
              'bech32': address_bech32,
              'crypto': {'cipher': 'aes-128-ctr',
                         'cipherparams': {'iv': hexlify(iv).decode()},
                         'ciphertext': hexlify(ciphertext).decode(),
                         'kdf': 'scrypt',
                         'kdfparams': {'dklen': 32,
                                       'n': 4096, 
                                       'p': 1,
                                       'r': 8,
                                       'salt': hexlify(salt).decode(),
                                       },
                         'mac': hexlify(mac).decode(),
                         }
              })


json_out = '/'.join((pem_path, address_bech32 + '.json'))

with open(json_out, 'w') as json_f:
    json_f.writelines(json)




