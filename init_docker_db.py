#!/usr/bin/env python3
import os
import sqlite3

def init_docker_db():
    """Initialiser la base de données pour Docker"""
    # Créer le répertoire data s'il n'existe pas
    os.makedirs('/app/data', exist_ok=True)
    
    # Chemin de la base de données
    db_path = '/app/data/monitoring.db'
    
    # Connexion et création des tables
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Table des machines
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS machines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            ip TEXT NOT NULL UNIQUE,
            statut TEXT DEFAULT 'Hors ligne',
            dernier_changement TEXT,
            duree_statut TEXT,
            services_actifs TEXT,
            info_systeme TEXT
        )
    ''')
    
    # Table des messages envoyés
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages_envoyes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            machine_id INTEGER,
            machine_nom TEXT,
            machine_ip TEXT,
            message TEXT,
            methode TEXT,
            port INTEGER,
            timestamp TEXT,
            statut TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
    print(f"Base de données initialisée: {db_path}")

if __name__ == "__main__":
    init_docker_db()
