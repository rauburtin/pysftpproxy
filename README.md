#pysftpproxy
An OpenSSH SFTP server wrapper written in python that acts as a proxy based on username

##Installing

* Installing redis on Ubuntu: 
```Shell
sudo apt-get install redis-server
```

##Features

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
	

