#!/bin/bash
#key used by the server part of the reverse proxy
export SFTPPROXY_PUBLICKEY_PATH="/home/rauburtin/.ssh/id_rsa.pub"
export SFTPPROXY_PRIVATEKEY_PATH="/home/rauburtin/.ssh/id_rsa"
#directory that will be used for the home directory
export SFTPPROXY_HOME="/root"
#the server listen to this port
export SFTPPROXY_PORT="5022"
#the userid and group id of the user that the server part of the proxy uses
export SFTPPROXY_USERID="1000"
export SFTPPROXY_GROUPID="1000"
#the user that the client part of the proxy uses to connect the remore ssh server
export SFTPPROXY_CLIENT_USER="root"
#redis configuration
export SFTPPROXY_REDIS_HOST="localhost"
export SFTPPROXY_REDIS_PORT="6379"
export SFTPPROXY_REDIS_DB="1"
#export SFTPPROXY_REDIS_PASSWORD="password"


