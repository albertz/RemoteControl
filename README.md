[RemoteControl](https://github.com/albertz/RemoteControl)
===============

RemoteControl is a client/server system to remotely control your computer. Originally, the main purpose was and is to control media/music players, although it is designed to be able to control the whole system.

The core of this project was the development of a generic secure communication protocol which uses the filesystem. The intention is to use services such as [Dropbox](https://www.dropbox.com/) or [Google Drive](https://drive.google.com/). This has the advantage that an existing infrastructure which works well can be reused and this project doesn't need to introduce an own server infrastructure. Technical descriptions about the implementation, how it works and the possibilities can be found [here](https://github.com/albertz/RemoteControl/blob/master/TechnicalDescription.md).

The current main functions of the client is to control the media keys (like play/pause, prev/next, volume up/down) on your computer (where the server daemon is run).

The server and the core is implemented in Python. The current client is an iOS application, implemented partly in ObjC and in Python.

Unfortunately, it turned out that the default Dropbox-based implementation is very slow. Too slow that this can be published in the AppStore for my taste. It takes about half-a-minute to do the initial handshake/connect and about 3 seconds to execute a command.

-- [Albert Zeyer](mailto:albzey@gmail.com)


