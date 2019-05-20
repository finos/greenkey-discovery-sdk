#!/bin/bash


GKT_USERNAME="gkt"
GKT_SECRETKEY="5f3d00b5b15884c280a390725a863941a68bfe55"
PORT=8005

docker run --rm -d \
	--name=formatter \
	-e GKT_API="https://scribeapi.greenkeytech.com/" \
	-e GKT_USERNAME=$GKT_USERNAME \
	-e GKT_SECRETKEY=$GKT_SECRETKEY \
	-p $PORT:8080 \
	"docker.greenkeytech.com/formatter:develop" && \
	echo "Formatter instance running on http://localhost:$PORT"




##!/bin/bash
#
#
#GKT_USERNAME="gkt"
#GKT_SECRETKEY="5f3d00b5b15884c280a390725a863941a68bfe55"
#PORT=8006
#NAME=formatter_ag
#
## default port for microservices is 8080
## to map to different internal port, need to add -e PORT=$PORT
#
#docker run --rm -d \
#        --name=$NAME \
#        -e GKT_API="https://scribeapi.greenkeytech.com/" \
#        -e GKT_USERNAME=$GKT_USERNAME \
#        -e GKT_SECRETKEY=$GKT_SECRETKEY \
#        -p $PORT:8080 \
#        "docker.greenkeytech.com/formatter:develop" && \
#        echo "Formatter instance running on http://localhost:$PORT"
