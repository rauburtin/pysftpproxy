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

* Docker Usage Example : Give to end users access to the volumes of a container in read/write with SFTP, for instance by using Filezilla

For instance, you want to cover this kind of use case ![Image of Docker usage](https://github.com/rauburtin/pysftpproxy/blob/master/examples/SFTPProxy.jpg)
Let's imagine that you want to give acess to the volume of a wordpress container.
You have a docker host (ex: 192.168.22.14).
On this host, you have a running wordpress container (ex: wordpress_wordpress_1) .

    1. Run a sshd container (look at https://docs.docker.com/examples/running_ssh_service/)

    2. Add the public key of the user who runs this reverse proxy to the authorized_keys file of the root user (use a ADD command in the Dockerfile to place the modified autorized_keys in /root/.ssh of the container)

    4. Generate a public and a private key for the end user (for example id_rsa and id_rsa.pub for the user usercontainer1). Generate also a ppk file for the private key (used by filezilla)

    5. Set the configuration in Redis
       You can look at the file  docker_redis.py in the examples folder.

       Basically, your redis database will have 2 keys:
       "pysftpproxy:pubkey:AAAAB3N...axDCYX" => usercontainer1
       "pysftpproxy:user:usercontainer1" => "remote":"192.168.22.14", "port":"32772"

    6. Set the envionment variables
       You can look at the file docker_properties.sh for the environment variables.

* Start the sftp proxy server
```Shell
bin/pysftpproxy
```

* Start a client such as sftp or filezilla and connect to the port of the reverse proxy (5022) in this sample
```Shell
sftp  -P 5022 localhost
```
	
##TODO
* Manage public and private keys for the client part of the proxy. At this time, the private and the public keys of the user who runs the code are used. 
* Describe the docker use case 
* Describe the data structure in Redis

