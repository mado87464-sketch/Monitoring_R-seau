import pytest
import sys
import os

# Ajouter le répertoire principal au path Python
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

try:
    from app import app, ping_host, valider_ip, etat_reel_machine
    APP_AVAILABLE = True
except ImportError:
    APP_AVAILABLE = False

class TestMonitoringApp:
    def test_app_exists(self):
        """Test que l'application Flask existe"""
        if APP_AVAILABLE:
            assert app is not None
        else:
            pytest.skip("App not available")
        
    def test_ping_host_invalid_ip(self):
        """Test ping avec IP invalide"""
        if APP_AVAILABLE:
            result = ping_host("999.999.999.999")
            assert result == "IP invalide"
        else:
            pytest.skip("App not available")
        
    def test_valider_ip_valid(self):
        """Test validation IP valide"""
        if APP_AVAILABLE:
            assert valider_ip("192.168.1.1") == True
            assert valider_ip("127.0.0.1") == True
            assert valider_ip("8.8.8.8") == True
        else:
            pytest.skip("App not available")
        
    def test_valider_ip_invalid(self):
        """Test validation IP invalide"""
        if APP_AVAILABLE:
            assert valider_ip("999.999.999.999") == False
            assert valider_ip("192.168.1") == False
            assert valider_ip("abc.def.ghi.jkl") == False
            assert valider_ip("") == False
        else:
            pytest.skip("App not available")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
