#pysftpproxy
An OpenSSH SFTP server wrapper written in python that acts as a proxy based on username

##Installing

* Installing redis on Ubuntu: 
```Shell
sudo apt-get install redis-server
```

##Features

This SFTP Proxy can be used to redirect sftp requests from a specific user to a particular remote server and port.

User => SftpProxy (CHECKS User Credentials, if OK it redirects) => RemoteServer:Port

This program can be useful to redirect sftp user requests to a sftp container in a docker host, so the user can access, in a secure way, to the volumes of a specific container

##Usage

* Insert some data in the Redis database, look at the examples directory
** Here, we just simulate the remote server as the localhost and the remote port to 22
* Start the sftp proxy server
```Shell
bin/pysftpproxy
```

* Start a client such as sftp
```Shell
sftp  -P 5022 localhost
```
	

