import sqlite3
from datetime import datetime

# Créer la base de données et la table
conn = sqlite3.connect('monitoring.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS machines (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT,
        ip TEXT,
        statut TEXT,
        dernier_changement TEXT,
        duree_statut TEXT
    )
''')

conn.commit()
conn.close()

print("Base de données SQLite créée avec succès !")
