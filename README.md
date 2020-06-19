# erdkeys

This are Flying Stone's little tools for converting between [elrond](https://elrond.com) wallet pem files and json 
keystores. Please be aware that the private key is written in plaintext in the pem file. The json 
keystores are much safer to use.

Use at your own risk and remember: if you run code you haven't read and understood, you can't be 
sure that it is not sending me your keys ;-)

## installing

Before insptalling erdkeys, make sure that `pip3` in installed. If you already installed `erdpy`, you should already have `pip3`.

`$ pip3 install erdkeys`

This will also install a couple of dependencies: the extremely cool [cryptography](https://pypi.org/project/cryptography/)
library and a small module to deal with bech32 addresses. 

## usage

`$ pem2json.py pem_file password`

`$ json2pem.py json_file password` 

For instance, one of my [Battle of Nodes](https://battleofnodes.com) wallet keystore is `erd1g2ufua664sxjvxmw5hh72he3xy6w4gk9l8e4lvfjeyh8d0jk7gdsfrpdu0.json` and I need to convert it to pem format for use with [erdpy](https://github.com/ElrondNetwork/erdpy):

`json2pem.py erd1g2ufua664sxjvxmw5hh72he3xy6w4gk9l8e4lvfjeyh8d0jk7gdsfrpdu0.json mYpAsSwOrD`

will produce a file `erd1g2ufua664sxjvxmw5hh72he3xy6w4gk9l8e4lvfjeyh8d0jk7gdsfrpdu0.pem` in the same directory. You will get an error in case the keystore is corrupted or you entered the wrong password. 

When creating a keystore with pem2json, the password must satisfy the same requirements as the official [wallet](https://wallet.elrond.com).

## license

MIT
