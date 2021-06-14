## Notes to self:
- docker image build -t **name** .
- docker image ls - see all docker images
- docker run -p **local port**:**container port** -d **container name**
    - docker run -p 5000:5000 -d docker_flask_task
        - -p is for port forwarding, map local port to docker port

### Volumes
- Stopping a container removes any data/state
- To persist & share data between containers, use **Volumes**
- A Volume is a dedicated folder on the host machine
- Inside a Volume, a container can create files that can be remounted into other containers 
- docker volume create **volume_name**
- docker run --mount source=**volume_name**,target=/stuff

### 1 Process per container

## Docker Compose
- docker compose up
- docker compose down