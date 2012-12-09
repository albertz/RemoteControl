Technical description
=====================

The [`fscomm`](#fscomm) module implements the communication over the filesystem. It is designed for peer-to-peer communication - it does not have a specific server-client design.

The [server daemon](#server) waits for incoming messages. It executes the Python code of known and verified peers.

The [client](#client) setups the needed Python code on the server and executes arbitrary commands on it - depending on what it wants to control.


## fscomm

Every peer registers itself as a device. Every communication is encrypted and signed with RSA and AES. A device has a type (string) and provides its public keys for encryption and signature verification. Every device can manage a set of message channels/connections with data sent bidirectional.


## server




## client

The client registers itself as a device, searches for some server device and sends the file [`media_keys.py`](https://github.com/albertz/RemoteControl/blob/master/pydata/media_keys.py). 

Then issues a command on the server which loads that file and executes some function.


