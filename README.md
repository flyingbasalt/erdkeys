# erdkeys

This are Flying Stone's little tools for converting between [elrond](https://elrond.com) wallet pem files and json 
keystores. Please be aware that the private key is written in plaintext in the pem file. The json 
keystores are much safer to use.

Use at your own risk and remember: if you run code you haven't read and understood, you can't be 
sure that it is not sending me your keys ;-)

## installing

`$ pip3 install erdkeys`

This will also install a couple of dependencies: the extremely cool [cryptography](https://pypi.org/project/cryptography/)
library and a small module to deal with bech32 addresses.

## usage

`$ ./pem2json.py pem_file password`

`$ ./json2pem.py json_file password`

The password must satisfy the same requirements as the official [wallet](https://wallet.elrond.com)

## license

MIT
