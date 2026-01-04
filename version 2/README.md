# Kafka KRaft cluster (3 controllers, 3 brokers) — `version 2`

Kurz: Diese Compose-Datei betreibt einen kleinen, produktionsnäheren KRaft-Cluster mit **3 Controllern** und **3 Brokern**. Unten findest du die exakten Befehle, um Controller zu starten, den Storage zu formatieren, Broker zu starten und einfache Tests durchzuführen.

---

## Voraussetzungen ✅
- Docker & Docker Compose installiert
- Arbeitsverzeichnis: `version 2`

---

## Schnellstart — exakte Befehle ▶️
1. In das Verzeichnis wechseln:

```powershell
cd 'version 2'
```

2. Controller starten (detached):

```powershell
docker compose up -d controller-1 controller-2 controller-3
```

3. (Nur beim ersten Setup) Storage für die Controller formatieren. Verwende die in der Compose-Datei gesetzte CLUSTER_ID (hier: `1L6g7nGhU-eAKfL--X25wo`). Führe das Format-Kommando für jeden Controller einmal aus:

```powershell
docker exec -it controller-1 bash -c "/usr/bin/kafka-storage format -t 1L6g7nGhU-eAKfL--X25wo -c /etc/kafka/kraft/server.properties"

docker exec -it controller-2 bash -c "/usr/bin/kafka-storage format -t 1L6g7nGhU-eAKfL--X25wo -c /etc/kafka/kraft/server.properties"

docker exec -it controller-3 bash -c "/usr/bin/kafka-storage format -t 1L6g7nGhU-eAKfL--X25wo -c /etc/kafka/kraft/server.properties"
```

> Hinweis: Formatieren darf nur bei Initialisierung geschehen. Wenn ein Controller bereits formatiert ist, NICHT erneut formatieren (Verlust der bestehenden Metadaten).

4. Controller-Logs prüfen (auf Quorum/Leader achten):

```powershell
docker logs -f controller-1
```

5. Broker starten:

```powershell
docker compose up -d broker-1 broker-2 broker-3
```

6. Broker-Logs prüfen:

```powershell
docker logs -f broker-1
```

7. Beispiel: Topic erstellen (Replication-Factor = 3):

```powershell
# von innerhalb eines Broker-Containers
docker exec -it broker-1 bash -c "kafka-topics --create --topic test --bootstrap-server broker-1:9092 --partitions 3 --replication-factor 3"

# alternativ, wenn du ein CLI lokal installiert hast:
# kafka-topics --create --topic test --bootstrap-server localhost:9092 --partitions 3 --replication-factor 3
```

8. Producer / Consumer testen:

```powershell
# Producer (host oder mapped port)
# lokal: kafka-console-producer --bootstrap-server localhost:9092 --topic test
# in container:
docker exec -it broker-1 bash -c "kafka-console-producer --bootstrap-server broker-1:9092 --topic test"

# Consumer (in container):
docker exec -it broker-1 bash -c "kafka-console-consumer --bootstrap-server broker-1:9092 --topic test --from-beginning"
```

---

## Ports & Mapping
- broker-1: host `localhost:9092` → container `29092` (PLAINTEXT_HOST)
- broker-2: host `localhost:9094` → container `29092` (PLAINTEXT_HOST)
- broker-3: host `localhost:9096` → container `29092` (PLAINTEXT_HOST)

Hinweis: Die Container-internen PLAINTEXT-Listener bleiben auf `9092`; der Host-Listener `PLAINTEXT_HOST` läuft in den Containern auf `29092` und wird an die Host-Ports `9092/9094/9096` weitergeleitet. Zum Testen vom Host nutze die oben genannten Host-Ports.

---

## Stop / Cleanup

```powershell
# stop + remove containers, networks, volumes (Container-Daten werden gelöscht)
docker compose down -v
```
