#!/bin/bash


GKT_USERNAME="gkt"
GKT_SECRETKEY="5f3d00b5b15884c280a390725a863941a68bfe55"

docker run --rm -d \
	--name=formatter \
	-e GKT_API="https://scribeapi.greenkeytech.com/" \
	-e GKT_USERNAME=$GKT_USERNAME \
	-e GKT_SECRETKEY=$GKT_SECRETKEY \
	-p 8005:8005 \
	"docker.greenkeytech.com/formatter:develop" && \
	echo "Formatter instance running on http://localhost:8002"
