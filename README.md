[RemoteControl](https://github.com/albertz/RemoteControl)
===============

RemoteControl is a client/server system to remotely control your computer. Originally, the main purpose was and is to control media/music players, although it is designed to be able to control the whole system.

The core of this project was the development of the communication protocol which uses the filesystem. The intention is to use services such as [Dropbox](https://www.dropbox.com/) or [Google Drive](https://drive.google.com/). This has the advantage that an existing infrastructure which works good can be reused and this project doesn't need to introduce an own server infrastructure. Technical descriptions about the implementation, how it works and the possibilities can be found [here](https://github.com/albertz/RemoteControl/blob/master/TechnicalDescription.md).

The current main functions of the client is to control the media keys (like play/pause, prev/next, volume up/down) on your computer (where the server daemon is run).

-- [Albert Zeyer](mailto:albzey@gmail.com)


