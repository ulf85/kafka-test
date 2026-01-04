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

### Validate that the topic was created (single-node)
`docker exec -it kafka kafka-topics --list --bootstrap-server localhost:9092`

### Describe that topic and see its partitions (single-node)
`docker exec -it kafka kafka-topics --bootstrap-server localhost:9092 --describe --topic new_orders`

### View all events in a topic (single-node)
`docker exec -it kafka kafka-console-consumer --bootstrap-server localhost:9092 --topic orders --from-beginning`

---

### If you are using the `version 2` KRaft cluster (3 controllers, 3 brokers)
Use broker containers or the mapped host ports (broker-1 -> localhost:9092, broker-2 -> localhost:9094, broker-3 -> localhost:9096).

- List topics (inside a broker container):
`docker exec -it broker-1 bash -c "kafka-topics --list --bootstrap-server broker-1:9092"`

- List topics (from the host, with local Kafka CLI):
`kafka-topics --list --bootstrap-server localhost:9092`

- Describe a topic (inside a broker container):
`docker exec -it broker-1 bash -c "kafka-topics --bootstrap-server broker-1:9092 --describe --topic new_orders"`

- Describe a topic (from the host):
`kafka-topics --bootstrap-server localhost:9092 --describe --topic new_orders`

- View events in a topic (inside a broker container):
`docker exec -it broker-1 bash -c "kafka-console-consumer --bootstrap-server broker-1:9092 --topic orders --from-beginning"`

- View events in a topic (from the host):
`kafka-console-consumer --bootstrap-server localhost:9092 --topic orders --from-beginning`

## Running the scripts
`python .\producer.py -n 5` # generates 5 random entries into a Kafka topic ('orders') (default is 10). When using the `version 2` cluster, the script defaults to multiple bootstrap servers: `localhost:9092,localhost:9094,localhost:9096` and will attempt to create the topic with replication-factor 3 if missing.
`python .\producer.py -n 5 --replication-factor 2 --partitions 3` # create topic with specific replication/partitions if missing
`python .\producer.py -n 5 --no-create-topic` # do not attempt to create topic
`python .\producer.py -n 5 --delay 2 --bootstrap localhost:9092,localhost:9094,localhost:9096` # override bootstrap list explicitly

`python .\tracker.py` # run the tracker (default bootstrap.servers=localhost:9092,localhost:9094,localhost:9096); start it in a second terminal
`python .\tracker.py --bootstrap localhost:9092,localhost:9094,localhost:9096 --topic orders --offset-reset earliest` # override bootstrap/ topic/offset reset behavior

Tip: both `producer.py` and `tracker.py` accept a `--bootstrap` option to provide multiple bootstrap servers for higher availability.