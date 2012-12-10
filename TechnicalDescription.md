Technical description
=====================

This describes the technic behind the communication over the filesystem to accomplish [RPC](http://en.wikipedia.org/wiki/Remote_procedure_call). Many other services like large file copying could be implemented, too.

## Why?

The intention is to use services such as [Dropbox](https://www.dropbox.com/) or [Google Drive](https://drive.google.com/). This has the advantage that an existing infrastructure which works good can be reused and this project doesn't need to introduce an own server infrastructure.


## Overview

The [`fscomm`](#fscomm) module implements the communication over the filesystem. It is designed for peer-to-peer communication - it does not have a specific server-client design.

The [server daemon](#server) waits for incoming messages. It executes the Python code of known and verified peers.

The [client](#client) setups the needed Python code on the server and executes arbitrary commands on it - depending on what it wants to control.


## [`fscomm`](https://github.com/albertz/RemoteControl/blob/master/common/fscomm.py)

Every peer registers itself as a device. Every communication is encrypted and signed with RSA and AES. A device has a type (string) and provides its public keys for encryption and signature verification. Every device can manage a set of message channels/connections with data sent bidirectional.

All serialization, the signing and encryption is done in the [`binstruct`](https://github.com/albertz/binstruct) module.

All files and directories created for communication are below some root directory which is by default `~/Dropbox/.AppCommunication/${appid}/` for now, where `${appid}` is `com.albertzeyer.RemoteEverywhere` in this case.

Every device gets its own directory `/dev-${devid}`. The file `publicKeys` in there defines the keys for signature verficitation and encryption. That is the only file which is not encrypted nor signed. There are the other files `name`, `appInfo` and `type` which are signed.

Channel connections are initialized by creating a file `/dev-${target_devid}/messages-from-${source_devid}/channel-${channelid}-init` which includes the intent of the connection. That file is signed by the source and encrypted for the destination. Then, for each package, a subsequent numbered files are created. When they got received, a specific `ack`-file for each package is created. Details can be found in the [source](https://github.com/albertz/RemoteControl/blob/master/common/fscomm.py).


## [`server`](https://github.com/albertz/RemoteControl/blob/master/server/server.py)




## [`client`](https://github.com/albertz/RemoteControl/blob/master/client/client.py)

The client registers itself as a device, searches for some server device and sends the file [`media_keys.py`](https://github.com/albertz/RemoteControl/blob/master/pydata/media_keys.py). 

Then issues a command on the server which loads that file and executes some function.


# Other applications

The whole design allows arbitrary data to be transfered. This project uses it for RPC. In theory, you could implement TCP or IP over it - although this would probably be way too slow as it turned out for this project.

Another application might be the transfer of large files. The files can be larger than what the underlying communication-filesystem supports.


