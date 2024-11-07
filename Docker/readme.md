# Instructions for docker

## First time 
1. Install docker if you dont have it allready: https://docs.docker.com/engine/install/
2. Replace [YOUR API KEY] in the docker-compose.yml file with your API key, without any quotations 
3. Open a terminal in this directory
4. Run: docker compose up -d
5. Post your request towards: http://localhost:8080
6. To stop everything: docker compose down

## Update container
1. docker compose down
2. docker pull sywor/considition2024:latest
3. docker compose up -d
