# Migration Docker Compose → Kubernetes

## 1. Installer un cluster local

Choisis-en un (minikube est le plus simple pour débuter) :

```bash
# minikube
brew install minikube        # ou l'équivalent pour ton OS
minikube start

# Active l'utilisation du registre Docker interne à minikube,
# pour pouvoir utiliser tes images buildées localement sans les pousser en ligne
eval $(minikube docker-env)
```

## 2. Builder les images DANS l'environnement du cluster

Important : si tu utilises minikube, il faut builder les images *après* avoir fait
`eval $(minikube docker-env)` dans ton terminal, sinon Kubernetes ne les trouvera pas.

```bash
docker build -t iot-backend:local ./backend
docker build -t iot-frontend:local ./frontend
```

## 3. Créer le ConfigMap pour Mosquitto

Contrairement à Compose (bind mount direct), Kubernetes a besoin que ton fichier
`mosquitto.conf` soit chargé en ConfigMap :

```bash
kubectl create configmap mosquitto-config \
  --from-file=./docker/mosquitto/config/mosquitto.conf \
  -n iot-platform
```
(Fais-le après avoir créé le namespace à l'étape 4, ou avant en ajoutant `--dry-run=client -o yaml` puis en l'ajoutant à tes fichiers.)

## 4. Appliquer tous les manifests

```bash
kubectl apply -f 00-namespace.yaml
kubectl apply -f 01-secrets-config.yaml
kubectl apply -f 02-postgres.yaml
kubectl apply -f 03-pgadmin.yaml
# crée le configmap mosquitto (étape 3) avant celui-ci
kubectl apply -f 04-mosquitto.yaml
kubectl apply -f 05-backend.yaml
kubectl apply -f 06-frontend.yaml
```

Ou tout en une fois (l'ordre des fichiers 00→06 suffit à respecter les dépendances) :
```bash
kubectl apply -f .
```

## 5. Vérifier que tout tourne

```bash
kubectl get pods -n iot-platform
kubectl get svc -n iot-platform
```

## 6. Accéder aux services

Avec minikube, les `NodePort` ne sont pas directement sur `localhost` :
```bash
minikube service frontend -n iot-platform   # ouvre le frontend dans le navigateur
minikube service backend -n iot-platform
minikube service pgadmin -n iot-platform
```

## 7. Utiliser Lens

1. Télécharge Lens : https://k8slens.dev
2. Lens détecte automatiquement ton kubeconfig (`~/.kube/config`), donc ton cluster
   minikube apparaît directement dans la liste au démarrage.
3. Clique dessus pour te connecter.
4. Dans le menu de gauche, sélectionne le namespace `iot-platform` (en haut) pour filtrer
   uniquement tes ressources.
5. Tu peux :
   - voir les **Pods**, leur statut, et cliquer dessus pour voir les **logs** en direct
   - ouvrir un **terminal** dans un pod (icône en haut à droite d'un pod) — équivalent de
     `docker exec`
   - voir les **Services**, leurs ports, et y accéder
   - éditer un manifest directement dans l'UI et l'appliquer (bouton "Save" = `kubectl apply`)
   - surveiller la conso CPU/RAM par pod en graphique

## Différences notables avec Compose

| Docker Compose | Kubernetes |
|---|---|
| `depends_on` | pas d'équivalent direct fiable → utiliser `readinessProbe` + init containers si besoin |
| bind mount `./docker/mosquitto/config` | `ConfigMap` (fichiers) + `PersistentVolumeClaim` (données) |
| `environment:` | `env:` / `envFrom: configMapRef` / `envFrom: secretRef` |
| réseau `iot-network` automatique | chaque `Service` crée son propre DNS interne (`<service>.<namespace>.svc.cluster.local`) |
| `ports: "5050:80"` | `Service` de type `NodePort`/`LoadBalancer`/`Ingress` |
| `docker compose up` | `kubectl apply -f .` |
| `docker compose down` | `kubectl delete -f .` ou `kubectl delete namespace iot-platform` |

## Pour la prod

Ce setup (NodePort, `imagePullPolicy: Never`, mots de passe en clair dans les secrets)
est pensé pour du **développement local**. Pour de la prod, il faudrait : un vrai registre
d'images (Docker Hub, GHCR...), un `Ingress` avec TLS, des secrets gérés via un vault, et
probablement un `StatefulSet` pour Postgres plutôt qu'un `Deployment`.
