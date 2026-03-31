# Docker pour Monitoring Réseau

## 🐳 Dockerisation de l'application

Cette application peut être facilement déployée avec Docker et Docker Compose.

## 📋 Prérequis

- Docker Desktop installé
- Docker Compose

## 🚀 Lancement rapide

### Option 1 : Docker Compose (recommandé)

```bash
# Cloner le dépôt
git clone https://github.com/VOTRE_NOM/monitoring-reseau.git
cd monitoring-reseau

# Lancer avec Docker Compose
docker-compose up -d

# Accéder à l'application
# Dashboard moderne : http://localhost:5000
# Version sécurisée : http://localhost:5001
```

### Option 2 : Docker seul

```bash
# Construire l'image
docker build -t monitoring-reseau .

# Lancer le conteneur
docker run -d \
  --name monitoring-app \
  -p 5000:5000 \
  -v $(pwd)/monitoring.db:/app/monitoring.db \
  monitoring-reseau
```

## 🏗️ Architecture Docker

### Services

1. **monitoring-app** (port 5000)
   - Version principale de l'application
   - Dashboard néon moderne
   - Base de données persistante

2. **monitoring-app-secure** (port 5001)
   - Version secondaire pour tests
   - Isolation complète
   - Données partagées

### Volumes

- `./data:/app/data` : Persistance des données
- `./monitoring.db:/app/monitoring.db` : Base de données SQLite

### Réseaux

- `monitoring-network` : Réseau isolé pour les services

## 🔧 Configuration

### Variables d'environnement

- `FLASK_ENV=production` : Mode production
- `FLASK_APP=app.py` : Application Flask

### Ports

- **5000** : Application principale
- **5001** : Application de test

## 📊 Monitoring dans Docker

L'application dans Docker conserve toutes ses fonctionnalités :

- ✅ **Ping réseau** : Compatible avec les conteneurs
- ✅ **Scan de ports** : Détection des services
- ✅ **Messages TCP/UDP/HTTP** : Communication réseau
- ✅ **Dashboard néon** : Interface moderne
- ✅ **Base de données** : Persistance des données

## 🔍 Commandes utiles

```bash
# Voir les logs
docker-compose logs -f monitoring-app

# Arrêter les services
docker-compose down

# Reconstruire les images
docker-compose build --no-cache

# Accéder au conteneur
docker exec -it monitoring-app bash

# Voir les ressources utilisées
docker stats monitoring-app
```

## 🐛 Dépannage

### Problèmes courants

1. **Port déjà utilisé**
   ```bash
   # Vérifier les ports utilisés
   netstat -tulpn | grep :5000
   
   # Changer le port dans docker-compose.yml
   ports:
     - "5002:5000"  # Utiliser 5002 au lieu de 5000
   ```

2. **Permissions de la base de données**
   ```bash
   # Donner les permissions correctes
   sudo chmod 666 monitoring.db
   ```

3. **Réseau inaccessible**
   ```bash
   # Vérifier le réseau Docker
   docker network ls
   docker network inspect monitoring-reseau_monitoring-network
   ```

## 🚀 Déploiement en production

### Configuration sécurisée

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  monitoring-app:
    build: .
    container_name: monitoring_prod
    ports:
      - "80:5000"  # Port 80 pour le public
    volumes:
      - ./data:/app/data
      - ./monitoring.db:/app/monitoring.db
    environment:
      - FLASK_ENV=production
    restart: always
    networks:
      - monitoring-network
```

### Lancement production

```bash
docker-compose -f docker-compose.prod.yml up -d
```

## 📈 Avantages du déploiement Docker

- 🔄 **Reproductibilité** : Identique partout
- 📦 **Isolation** : Pas de conflits de dépendances
- 🚀 **Déploiement rapide** : Une seule commande
- 🔒 **Sécurité** : Environnement isolé
- 📊 **Scalabilité** : Plusieurs instances
- 💾 **Persistance** : Données conservées

## 🌐 Accès réseau

Depuis Docker, l'application peut surveiller :

- ✅ **Machines sur le réseau hôte**
- ✅ **Services locaux** (si ports exposés)
- ✅ **Conteneurs Docker** (sur le même réseau)
- ✅ **Services externes** (internet)

Pour surveiller le réseau hôte complet, utilisez :

```bash
docker run --net=host monitoring-reseau
```

## 📝 Notes importantes

- L'application utilise **SQLite** pour la simplicité
- Les données sont **persistantes** grâce aux volumes
- Le **mode debug** est désactivé en production
- Les **logs** sont accessibles via `docker-compose logs`

---

**🐳 Votre application de monitoring réseau est maintenant prête pour Docker !**
