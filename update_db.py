import sqlite3
from datetime import datetime

# Mettre à jour la base de données existante
conn = sqlite3.connect('monitoring.db')
cursor = conn.cursor()

# Ajouter les nouvelles colonnes si elles n'existent pas
try:
    cursor.execute('ALTER TABLE machines ADD COLUMN dernier_changement TEXT')
    print("Colonne 'dernier_changement' ajoutée")
except:
    print("Colonne 'dernier_changement' existe déjà")

try:
    cursor.execute('ALTER TABLE machines ADD COLUMN duree_statut TEXT')
    print("Colonne 'duree_statut' ajoutée")
except:
    print("Colonne 'duree_statut' existe déjà")

try:
    cursor.execute('ALTER TABLE machines ADD COLUMN services_actifs TEXT')
    print("Colonne 'services_actifs' ajoutée")
except:
    print("Colonne 'services_actifs' existe déjà")

try:
    cursor.execute('ALTER TABLE machines ADD COLUMN info_systeme TEXT')
    print("Colonne 'info_systeme' ajoutée")
except:
    print("Colonne 'info_systeme' existe déjà")

# Créer la table des messages envoyés
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
        statut TEXT,
        FOREIGN KEY (machine_id) REFERENCES machines (id)
    )
''')

# Créer la table des téléphones détectés
cursor.execute('''
    CREATE TABLE IF NOT EXISTS telephones_detectes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ip TEXT,
        mac TEXT,
        type_appareil TEXT,
        fabricant TEXT,
        services TEXT,
        confiance TEXT,
        timestamp TEXT
    )
''')

print("Table 'telephones_detectes' créée avec succès")

print("Table 'messages_envoyes' créée avec succès")

# Initialiser les nouvelles colonnes pour les machines existantes
cursor.execute("SELECT id FROM machines")
machines = cursor.fetchall()

for machine in machines:
    machine_id = machine[0]
    cursor.execute("SELECT dernier_changement FROM machines WHERE id = ?", (machine_id,))
    result = cursor.fetchone()
    
    if not result or not result[0]:
        maintenant = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute("UPDATE machines SET dernier_changement = ?, duree_statut = '0 min', services_actifs = 'Non scanné', info_systeme = 'Non disponible' WHERE id = ?", 
                      (maintenant, machine_id))

conn.commit()
conn.close()

print("Base de données mise à jour avec succès !")
