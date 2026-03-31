# Monitoring Réseau

Une application Flask de monitoring réseau avec dashboard moderne et design néon.

## Fonctionnalités

- 🖥️ **Dashboard moderne** avec design néon dark
- 📊 **Métriques en temps réel** des machines du réseau
- 🔍 **Détection automatique** des services et ports
- 📡 **Envoi de messages** via TCP/UDP/HTTP
- 📈 **Graphiques visualisés** de l'état du réseau
- 🔄 **Auto-rafraîchissement** toutes les 30 secondes
- 📱 **Design responsive** avec layout latéral

## Captures d'écran

### Dashboard Moderne
![Dashboard](https://via.placeholder.com/800x400/1a1a2e/00d4ff?text=Dashboard+Moderne)

### Vue Classique
![Vue Classique](https://via.placeholder.com/800x400/ffffff/667eea?text=Vue+Classique)

## Installation

1. **Cloner le dépôt**
   ```bash
   git clone https://github.com/VOTRE_NOM/monitoring-reseau.git
   cd monitoring-reseau
   ```

2. **Installer les dépendances**
   ```bash
   pip install flask psutil requests
   ```

3. **Initialiser la base de données**
   ```bash
   python init_db.py
   ```

4. **Lancer l'application**
   ```bash
   python app.py
   ```

5. **Accéder à l'application**
   - Dashboard moderne : http://127.0.0.1:5000/
   - Vue classique : http://127.0.0.1:5000/classic

## Utilisation

### Ajouter une machine
1. Remplir le nom et l'adresse IP
2. Cliquer sur "Ajouter"
3. L'application testera automatiquement la connectivité

### Envoyer un message
1. Sélectionner une machine en ligne
2. Choisir le protocole (TCP/UDP/HTTP)
3. Taper votre message et envoyer

### Voir les métriques
- Machines actives
- Problèmes détectés
- Services en cours d'exécution
- Taux de disponibilité

## Technologies

- **Backend** : Flask (Python)
- **Frontend** : HTML5, CSS3, JavaScript
- **Base de données** : SQLite
- **Monitoring** : Ping, scan de ports
- **Design** : Glassmorphism néon, animations CSS3

## Structure du projet

```
monitoring-reseau/
├── app.py              # Application Flask principale
├── init_db.py          # Initialisation de la BDD
├── update_db.py        # Mises à jour du schéma
├── templates/
│   ├── dashboard.html  # Dashboard moderne
│   ├── index.html      # Vue classique
│   └── messages.html   # Historique des messages
├── monitoring.db       # Base de données SQLite
└── README.md           # Ce fichier
```

## API Endpoints

- `GET /` - Dashboard moderne
- `GET /classic` - Vue classique
- `GET /messages` - Historique des messages
- `POST /add` - Ajouter une machine
- `POST /send_message/<id>` - Envoyer un message
- `POST /delete/<id>` - Supprimer une machine

## Configuration

L'application utilise une configuration par défaut :
- Port : 5000
- Hôte : 0.0.0.0 (accessible depuis le réseau)
- Mode debug : Activé

## Contribuer

1. Forker le projet
2. Créer une branche (`git checkout -b feature/nouvelle-fonctionnalite`)
3. Commiter les changements (`git commit -am 'Ajouter nouvelle fonctionnalité'`)
4. Pusher sur la branche (`git push origin feature/nouvelle-fonctionnalite`)
5. Créer une Pull Request

## Licence

Ce projet est sous licence MIT.

## Auteur

[VOTRE NOM] - [VOTRE EMAIL]

## Remerciements

- Flask pour le framework web
- Bootstrap pour l'inspiration design
- La communauté Python pour les excellentes bibliothèques
