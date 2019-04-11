


docker swarm leave --force && docker swarm init && docker stack deploy -c docker-compose.yaml chat_quotes 

curl -X GET localhost:8003/ping

curl http://localhost:8003/ping

# Use `chat_slack` to pull chats and send to `discovery`
- chats: quotes vs. not quotes x formatted vs. unformatted

- unformatted: chats used for `quotes` interpreter (discovery sdk) and `textclassifiers`
  - gcloud bucket: 
 
- formatted: Selerity chat data for quotes; generated not-quotes with similar
  entities


# Set up swarm

```bash

docker swarm init

# chat_quotes is arbitrary name for stack; prefixed to names of all containers in stack
docker stack deploy -c docker-compose.yaml --with-registry-auth chat_quotes

# to see stack
docker stack ps chat_quotes

# check health of nodes         --> tells you IDs, PORTs, names, mode, number of replicas, image name
docker stack services chat_quotes

# run jobs via batch process (8 or 16 -> number of replicas)
# ls accent_data/*.mp3 | parallel -j 8 ./batch_process.sh

# remove all containers in swarm; if you do this, start again with docker swarm init
docker swarm leave --force

# to see if container is accepting jobs
docker logs -f container_name_or_code  # docker logs -f 1b1
```


# Useful Code
###  https://github.com/greenkeytech/scribe/blob/develop/deployments/swarm/transcription-machine/launch
`watch 'cat accent_data/*.json | grep transcription_time | wc -l'`


# Docker documentation for Swarm deployment & checks
###  https://docs.docker.com/engine/reference/commandline/stack_deploy#description
### https://docs.docker.com/engine/reference/commandline/stack_deploy#usage
