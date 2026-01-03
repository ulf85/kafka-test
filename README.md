# kafka-crash-course
based on
- https://gitlab.com/twn-youtube/kafka-crash-course
- https://www.youtube.com/watch?v=B7CwU_tNYIE

## Prerequisites
- Python is installed
- Docker Desktop (with Docker and Docker Compose) is installed

### Install confluent-kafka dependency
`pip3 install confluent-kafka`

## Starting Docker Compose
(with the defined Docker image and volume)  
`docker compose up -d`  
`docker compose ps` # check  
`docker compose down -v` # if you want to stop Docker Compose later

### Validate that the topic was created in kafka container
`docker exec -it kafka kafka-topics --list --bootstrap-server localhost:9092`

### Describe that topic and see its partitions
`docker exec -it kafka kafka-topics --bootstrap-server localhost:9092 --describe --topic new_orders`

### View all events in a topic
`docker exec -it kafka kafka-console-consumer --bootstrap-server localhost:9092 --topic orders --from-beginning`

## Running the scripts
`python .\producer.py -n 5` # generates 5 random entries into a Kafka topic ('orders') (default is 10)
`python .\producer.py -n 5 --delay 2` # with additionally 2 seconds delay (default is 0.1)
`python .\tracker.py` # preferably start it in a second terminal