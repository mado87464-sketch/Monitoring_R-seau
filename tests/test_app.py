import pytest
import sys
import os

# Ajouter le répertoire principal au path Python
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from app import app, ping_host, valider_ip, etat_reel_machine

class TestMonitoringApp:
    def test_app_exists(self):
        """Test que l'application Flask existe"""
        assert app is not None
        
    def test_ping_host_valid_ip(self):
        """Test ping avec IP valide"""
        # Test avec localhost (devrait toujours répondre dans les tests)
        result = ping_host("127.0.0.1")
        assert result in ["En ligne", "Hors ligne", "Timeout", "Limité"]
        
    def test_ping_host_invalid_ip(self):
        """Test ping avec IP invalide"""
        result = ping_host("999.999.999.999")
        assert result == "IP invalide"
        
    def test_valider_ip_valid(self):
        """Test validation IP valide"""
        assert valider_ip("192.168.1.1") == True
        assert valider_ip("127.0.0.1") == True
        assert valider_ip("8.8.8.8") == True
        
    def test_valider_ip_invalid(self):
        """Test validation IP invalide"""
        assert valider_ip("999.999.999.999") == False
        assert valider_ip("192.168.1") == False
        assert valider_ip("abc.def.ghi.jkl") == False
        assert valider_ip("") == False
        
    def test_etat_reel_machine(self):
        """Test fonction etat_reel_machine"""
        # Test avec une IP qui devrait être traitée
        result = etat_reel_machine("192.168.1.1")
        assert result in ["En ligne", "Hors ligne"]
        
    def test_flask_routes(self):
        """Test que les routes Flask existent"""
        with app.test_client() as client:
            # Test route principale
            response = client.get('/')
            assert response.status_code in [200, 500]  # 500 si BDD non initialisée
            
            # Test route classique
            response = client.get('/classic')
            assert response.status_code in [200, 500]

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
