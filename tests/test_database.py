import pytest
import tempfile
import os
import sqlite3
import sys

# Ajouter le répertoire principal au path Python
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from app import app, get_db_connection

class TestDatabase:
    def test_database_connection(self):
        """Test connexion à la base de données"""
        with app.app_context():
            conn = get_db_connection()
            assert conn is not None
            conn.close()
            
    def test_database_tables_creation(self):
        """Test création des tables"""
        with app.app_context():
            # Créer une base de données temporaire
            with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as tmp_db:
                os.environ['DATABASE_PATH'] = tmp_db.name
                
                # Initialiser la base de données
                from init_docker_db import init_docker_db
                init_docker_db()
                
                # Vérifier que les tables existent
                conn = sqlite3.connect(tmp_db.name)
                cursor = conn.cursor()
                
                # Vérifier table machines
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='machines'")
                machines_table = cursor.fetchone()
                assert machines_table is not None
                
                # Vérifier table messages_envoyes
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='messages_envoyes'")
                messages_table = cursor.fetchone()
                assert messages_table is not None
                
                conn.close()
                
    def test_database_insert_retrieve(self):
        """Test insertion et récupération de données"""
        with app.app_context():
            # Créer une base de données temporaire
            with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as tmp_db:
                os.environ['DATABASE_PATH'] = tmp_db.name
                
                # Initialiser la base de données
                from init_docker_db import init_docker_db
                init_docker_db()
                
                # Insérer une machine de test
                conn = sqlite3.connect(tmp_db.name)
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO machines (nom, ip, statut) VALUES (?, ?, ?)",
                    ("Test Machine", "192.168.1.100", "Hors ligne")
                )
                conn.commit()
                
                # Récupérer la machine
                cursor.execute("SELECT nom, ip, statut FROM machines WHERE nom = ?", ("Test Machine",))
                machine = cursor.fetchone()
                
                assert machine is not None
                assert machine[0] == "Test Machine"
                assert machine[1] == "192.168.1.100"
                assert machine[2] == "Hors ligne"
                
                conn.close()

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
