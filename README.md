# 🖥️ Monitoring Réseau

Application de monitoring réseau avec détection de connectivité en temps réel utilisant Flask et Docker.

## 🚀 Démarrage rapide

### Avec Docker (Recommandé)

1. **Clonez le dépôt :**
```bash
git clone https://github.com/mado87464-sketch/Monitoring_R-seau.git
cd Monitoring_R-seau
```

2. **Démarrez avec Docker Compose :**
```bash
docker-compose up -d
```

3. **Accédez à l'application :**
- 🌐 **Interface web** : http://localhost:5002
- 📊 **Monitoring** en temps réel des machines

### Avec Docker Hub

L'image est disponible sur Docker Hub :

```bash
docker pull mado87464/monitoring-reseau:latest
docker run -d -p 5002:5000 --name monitoring-app mado87464/monitoring-reseau:latest
```

## 📋 Fonctionnalités

- ✅ **Détection de connectivité** avec ping simple
- ✅ **États en temps réel** : En ligne / Hors ligne
- ✅ **Interface web** moderne et responsive
- ✅ **Base de données** SQLite pour persistance
- ✅ **Support Docker** pour déploiement facile
- ✅ **Monitoring** de plusieurs machines simultanément
- ✅ **Messages** UDP/TCP/HTTP vers machines
- ✅ **Suppression** de machines
- ✅ **Informations système** détaillées

## 🐳 Architecture Docker

### Services
- **monitoring-app** : Application Flask (port 5002)
- **Base de données** : SQLite persistante
- **Réseau** : Isolé pour sécurité

### Volumes
- `./data:/app/data` : Persistance des données

### Ports
- **5002** : Interface web

## 🔧 Configuration

### Variables d'environnement
- `DATABASE_PATH` : Chemin de la base de données (défaut : `/app/data/monitoring.db`)

### Ports personnalisables
Modifiez `docker-compose.yml` pour changer les ports :
```yaml
ports:
  - "VOTRE_PORT:5000"
```

## 📊 Utilisation

1. **Ajoutez une machine :**
   - Nom : Identifiant de la machine
   - IP : Adresse IP à surveiller

2. **Vérifiez le statut :**
   - 🟢 **En ligne** : Machine répond au ping
   - 🔴 **Hors ligne** : Machine inaccessible

3. **Actions disponibles :**
   - 📤 Envoyer des messages
   - 🗑️ Supprimer des machines
   - 🔄 Actualiser en temps réel

## 🛠️ Développement

### Structure du projet
```
Monitoring_R-seau/
├── app.py                 # Application Flask principale
├── Dockerfile             # Configuration Docker
├── docker-compose.yml     # Services multi-conteneurs
├── requirements.txt       # Dépendances Python
├── init_docker_db.py    # Initialisation BDD Docker
├── templates/           # Templates HTML
│   ├── index.html      # Interface principale
│   └── dashboard.html # Template alternatif
├── data/               # Base de données SQLite
└── README.md          # Documentation
```

### Lancer en développement
```bash
# Installation dépendances
pip install -r requirements.txt

# Lancement application
python app.py
```

## 📝 API

### Endpoints
- `GET /` : Interface principale
- `GET /classic` : Vue classique
- `POST /add` : Ajouter une machine
- `POST /delete/<id>` : Supprimer une machine
- `POST /send_message/<id>` : Envoyer un message

## 🔒 Sécurité

- **Conteneur isolé** : Pas d'accès root
- **Réseau dédié** : Communication contrôlée
- **Base de données locale** : Pas d'exposition externe

## 🐛 Dépannage

### Problèmes courants
1. **Port déjà utilisé** : Changez le port dans `docker-compose.yml`
2. **Permission refusée** : Vérifiez les droits sur le dossier `data/`
3. **Machine inaccessible** : Vérifiez la configuration réseau

### Logs Docker
```bash
docker-compose logs -f
```

## 🤝 Contribuer

1. Fork le projet
2. Créer une branche (`git checkout -b feature/nouvelle-fonctionnalite`)
3. Commiter (`git commit -am 'Ajout nouvelle fonctionnalité'`)
4. Pusher (`git push origin feature/nouvelle-fonctionnalite`)
5. Créer une Pull Request

## 📄 Licence

Ce projet est sous licence MIT.

## 🙏 Remerciements

- Flask : Framework web Python
- Docker : Conteneurisation
- SQLite : Base de données légère
- psutil : Informations système

---

**Développé avec ❤️ par [mado87464-sketch](https://github.com/mado87464-sketch)**
