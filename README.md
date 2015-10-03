#pysftpproxy
An OpenSSH SFTP server wrapper written in python that acts as a proxy based on username

##Installing

* Installing redis on Ubuntu: 
```Shell
sudo apt-get install redis-server
```

##Features

This SFTP Proxy can be used to redirect sftp request from a specific user to a specific remote server and port

User => SEFTP PROXY (Check User Credentials, if OK it redirects to) => RemoteServer:Port

This configuration can be usefull to redirect user to a sftp container in a docker host

##Usage

* Insert some data in the Redis database, look at the examples directory
* Start the sftp proxy server
```Shell
bin/pysftpproxy
```

* Start a client such as sftp
```Shell
sftp  -P 5022 localhost
```
	

