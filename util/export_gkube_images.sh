#!/usr/bin/env bash

# export discovery image
discovery_image=$(gkube kubectl get deploy gk-discovery -o go-template='{{range .spec.template.spec.containers}}{{if eq "discovery" .name}}{{.image}}{{end}}{{end}}')
docker exec default-gkube-server ctr images export - "$discovery_image" | docker load

# export init_discovery image
init_discovery_image=$(gkube kubectl get deploy gk-discovery -o go-template='{{range .spec.template.spec.initContainers}}{{if eq "initdiscovery" .name}}{{.image}}{{end}}{{end}}')
docker exec default-gkube-server ctr images export - "$init_discovery_image" | docker load

# export busybox
busybox_image=$(docker exec default-gkube-server ctr images list | grep library/busybox: | awk '{print $1}')
docker exec default-gkube-server ctr images export - "$busybox_image" | docker load

DISCOVERY_TAG=$(echo "$discovery_image" | sed 's/docker.greenkeytech.com\/discovery://g')
INIT_DISCOVERY_TAG=$(echo "$init_discovery_image" | sed 's/docker.greenkeytech.com\/greenkey-discovery-sdk-private://g')
BUSYBOX_TAG=$(echo "$busybox_image" | sed 's/docker.io\/library\/busybox://g')

# update the client.env file to reflect your updated image tags
sed -i '/^DISCOVERY_TAG/c DISCOVERY_TAG='"$DISCOVERY_TAG" client.env
sed -i '/^INIT_DISCOVERY_TAG/c INIT_DISCOVERY_TAG='"$INIT_DISCOVERY_TAG" client.env
sed -i '/^BUSYBOX_TAG/c BUSYBOX_TAG='"$BUSYBOX_TAG" client.env
