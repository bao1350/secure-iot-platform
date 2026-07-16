# Secure IoT Platform

## Présentation

Cette plateforme sécurise les échanges IoT avec une API FastAPI, un broker MQTT Mosquitto et une interface frontend. Le projet est conçu pour fonctionner dans Docker avec HTTPS pour l’API et TLS optionnel pour MQTT.

## Convention MQTT

Toutes les mesures sont publiées sur le topic `iot/sensors/{sensor_id}/measures`.

Exemple pour le capteur `1` : `iot/sensors/1/measures`.

Le message JSON doit contenir le même `sensor_id` que celui présent dans le topic :

```json
{
  "sensor_id": 1,
  "temperature": 22.3,
  "humidity": 45,
  "battery": 96
}
```

## Prérequis

- Docker
- Docker Compose
- (optionnel) Git
- (optionnel) Node.js + npm si vous souhaitez lancer le frontend hors Docker
- (optionnel) Python si vous souhaitez lancer le backend hors Docker

## Structure du projet

- `backend/` : API FastAPI, base de données, MQTT client et logique métier
- `frontend/` : application web qui consomme l’API
- `docker/` : configuration Mosquitto et certificats
- `docker-compose.yml` : orchestration de tous les services

## 1. Lancer le projet avec Docker Compose

Les migrations de base de données sont appliquées automatiquement au démarrage du backend. La première migration crée une base neuve ou renforce une base créée par l'ancienne version. Les anciennes mesures sans `sensor_id` sont conservées dans `legacy_invalid_measures`, car elles ne peuvent pas appartenir à un capteur actif. Avant toute mise à niveau, réalisez une sauvegarde ; les autres valeurs nulles, hors plage ou relations incohérentes restent bloquantes.

Avant le premier lancement, copiez `.env.example` vers `.env`, puis remplacez toutes les valeurs d'exemple par des secrets forts. Le fichier `.env` est ignoré par Git.

### 1.1. Générer les certificats pour le backend

- Sur PowerShell Windows :

```powershell
New-Item -ItemType Directory -Force backend\certs
docker run --rm -v ${PWD}/backend/certs:/certs -w /certs alpine sh -c "apk add --no-cache openssl && openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout key.pem -out cert.pem -subj '/CN=localhost'"
```

- Sur Linux / macOS / WSL :

```bash
mkdir -p backend/certs
docker run --rm -v $(pwd)/backend/certs:/certs -w /certs alpine sh -c "apk add --no-cache openssl && openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout key.pem -out cert.pem -subj '/CN=localhost'"
```

> Si vous préférez, utilisez un OpenSSL local et placez `key.pem` et `cert.pem` dans `backend/certs`.

### 1.2. Générer les certificats pour Mosquitto (optionnel)

- Sur PowerShell Windows :

```powershell
New-Item -ItemType Directory -Force docker\mosquitto\certs
docker run --rm -v ${PWD}/docker/mosquitto/certs:/certs -w /certs alpine sh -c "apk add --no-cache openssl && openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout server.key -out server.crt -subj '/CN=localhost'"
```

- Sur Linux / macOS / WSL :

```bash
mkdir -p docker/mosquitto/certs
docker run --rm -v $(pwd)/docker/mosquitto/certs:/certs -w /certs alpine sh -c "apk add --no-cache openssl && openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout server.key -out server.crt -subj '/CN=localhost'"
chmod 644 docker/mosquitto/certs/server.key
```

### 1.3. Démarrer tous les services

```bash
docker compose up --build
```

L’API sera disponible sur :

- `https://localhost:8000`
- frontend : `http://localhost:5173`

### 1.4. Arrêter les services

```bash
docker compose down
```

## 2. Vérifier que l’API fonctionne en HTTPS

- Sur Linux/macOS ou dans WSL :

```bash
curl -k https://localhost:8000/
```

- Sur PowerShell sous Windows :

```powershell
curl.exe -k https://localhost:8000/
```

> Dans PowerShell, `curl` est un alias pour `Invoke-WebRequest`. Utilisez `curl.exe` pour le vrai client `curl`.

Le `-k` est nécessaire pour le certificat auto-signé.

## 3. Lancer le projet en mode développement

### 3.1. Backend local

Depuis `backend/` :

```bash
python -m venv venv
source venv/bin/activate    # Linux/macOS
venv\Scripts\Activate.ps1 # PowerShell
pip install -r requirements.txt
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### 3.2. Frontend local

Depuis `frontend/` :

```bash
npm install
npm run dev -- --host 0.0.0.0 --port 5173
```

Si l’API est en local, définissez `VITE_API_URL` sur `http://localhost:8000` dans votre shell ou `.env`.

## 4. HTTPS / TLS

### 4.1. Backend HTTPS

Le backend démarre avec `uvicorn` en HTTPS via les certificats :

- `backend/certs/cert.pem`
- `backend/certs/key.pem`

### 4.2. Mosquitto TLS

Pour MQTT, la configuration Mosquitto est activée sur le port `8883` en TLS avec :

- `docker/mosquitto/certs/server.crt`
- `docker/mosquitto/certs/server.key`

### 4.3. Remarques sur les certificats

- Le certificat de développement est auto-signé, donc le navigateur affichera un avertissement.
- En production, utilisez un certificat valide délivré par une autorité de confiance.
- Pour un déploiement sécurisé, placez un proxy TLS devant FastAPI : `nginx`, `traefik`, `Caddy`, etc.

## 5. Notes de sécurité

- Le backend utilise `uvicorn` en HTTPS avec `backend/certs/key.pem` et `backend/certs/cert.pem`.
- Pour un environnement de production, remplacez le certificat auto-signé par un certificat valide et utilisez un proxy TLS ou une solution de gestion de certificats.
  - Exemple : placez `nginx`, `traefik`, `Caddy` ou un load balancer devant FastAPI pour gérer TLS.
  - Exemple de certificat valide : Let's Encrypt ou un certificat fourni par votre CA.
- Pour MQTT, activez TLS séparément dans Mosquitto si vous souhaitez sécuriser aussi les communications MQTT.
  - Cela implique de configurer `listener 8883`, `cafile`, `certfile` et `keyfile` dans `docker/mosquitto/config/mosquitto.conf`.
