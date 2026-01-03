# kafka-crash-course

## Voraussetzungen
- Python ist installiert
- Docker Desktop (mit Docker und Docker Compose) ist installiert

### Install confluent-kafka dependency
`pip3 install confluent-kafka`

## Start von Docker Compose
(mit den definierten Docker Image und Volume)  
`docker compose up -d`  
`docker compose ps` # check  
`docker compose down -v` # wenn man später Docker Compose wieder stoppen möchte

### Validate that the topic was created in kafka container
`docker exec -it kafka kafka-topics --list --bootstrap-server localhost:9092`

### Describe that topic and see its partitions
`docker exec -it kafka kafka-topics --bootstrap-server localhost:9092 --describe --topic new_orders`

### View all events in a topic
`docker exec -it kafka kafka-console-consumer --bootstrap-server localhost:9092 --topic orders --from-beginning`

## Aufruf der Skripte
`python .\producer.py -n 5` # erzeugt 5 zufällige Einträge in einem Kafka Topic ('orders')  
`python .\tracker.py` # am besten in einem zweiten Terminal starten