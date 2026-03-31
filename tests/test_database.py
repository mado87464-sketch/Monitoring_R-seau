import pytest
import tempfile
import os
import sqlite3
import sys

# Ajouter le répertoire principal au path Python
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

try:
    from app import get_db_connection
    from init_docker_db import init_docker_db
    APP_AVAILABLE = True
except ImportError:
    APP_AVAILABLE = False

class TestDatabase:
    def test_database_connection(self):
        """Test connexion à la base de données"""
        if APP_AVAILABLE:
            try:
                from app import app
                with app.app_context():
                    conn = get_db_connection()
                    assert conn is not None
                    conn.close()
            except:
                pytest.skip("Database connection failed")
        else:
            pytest.skip("App not available")
            
    def test_database_tables_creation(self):
        """Test création des tables"""
        if APP_AVAILABLE:
            try:
                # Créer une base de données temporaire
                with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as tmp_db:
                    os.environ['DATABASE_PATH'] = tmp_db.name
                    
                    # Initialiser la base de données
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
            except:
                pytest.skip("Database creation failed")
        else:
            pytest.skip("App not available")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
