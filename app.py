from flask import Flask, render_template, request, redirect, flash, get_flashed_messages, jsonify
import os
import subprocess
import sqlite3
from datetime import datetime, timedelta
import re
import socket
import requests
import psutil
import threading
import time
import json

app = Flask(__name__)
app.secret_key = 'votre_cle_secrete_ici'

# Connexion à la base de données
def get_db_connection():
    # Utiliser le chemin de la base de données depuis les variables d'environnement ou chemin par défaut
    db_path = os.environ.get('DATABASE_PATH', '/app/data/monitoring.db')
    conn = sqlite3.connect(db_path, timeout=30.0)  # Timeout augmenté à 30 secondes
    conn.row_factory = sqlite3.Row
    # Activer WAL mode pour éviter les conflits
    conn.execute('PRAGMA journal_mode=WAL')
    # Activer les foreign keys
    conn.execute('PRAGMA foreign_keys=ON')
    # Désactiver le mode synchrone pour éviter les blocages
    conn.execute('PRAGMA synchronous=NORMAL')
    return conn

# Calculer la durée depuis le dernier changement de statut
def calculer_duree(dernier_changement_str):
    try:
        dernier_changement = datetime.strptime(dernier_changement_str, '%Y-%m-%d %H:%M:%S')
        maintenant = datetime.now()
        duree = maintenant - dernier_changement
        
        if duree.days > 0:
            return f"{duree.days}j {duree.seconds // 3600}h"
        elif duree.seconds >= 3600:
            return f"{duree.seconds // 3600}h {duree.seconds % 3600 // 60}min"
        elif duree.seconds >= 60:
            return f"{duree.seconds // 60}min"
        else:
            return f"{duree.seconds}s"
    except:
        return "Inconnu"

# Valider l'adresse IP
def valider_ip(ip):
    # Pattern regex pour IPv4
    pattern = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
    return re.match(pattern, ip) is not None

# Vérifier si une machine est en ligne
def ping_host(ip):
    try:
        # Vérifier si l'IP est valide
        if not valider_ip(ip):
            return "IP invalide"
        
        # Utiliser la syntaxe Linux pour le ping (conteneur Docker) avec timeout plus court
        output = subprocess.run(["ping", "-c", "1", "-W", "1", ip], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=2)
        
        if output.returncode == 0:
            return "En ligne"  # Si le ping répond, la machine est en ligne
        else:
            # Analyser la sortie pour des messages d'erreur spécifiques
            stderr_text = output.stderr.decode('utf-8', errors='ignore').lower()
            stdout_text = output.stdout.decode('utf-8', errors='ignore').lower()
            
            if "destination host unreachable" in stderr_text or "destination host unreachable" in stdout_text:
                return "Hôte inaccessible"
            elif "request timed out" in stderr_text or "request timed out" in stdout_text or "100% packet loss" in stdout_text:
                return "Timeout"
            elif "name or service not known" in stderr_text or "name or service not known" in stdout_text:
                return "Hôte introuvable"
            else:
                return "Hors ligne"
    except subprocess.TimeoutExpired:
        return "Timeout"
    except Exception as e:
        return f"Erreur: {str(e)[:30]}"

# Vérification avancée de connectivité (test de port)
def verifier_connectivite_reelle(ip, port=80, timeout=3):
    """Vérifie si la machine répond réellement aux connexions"""
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((ip, port))
        sock.close()
        
        if result == 0:
            return True  # La machine répond réellement
        else:
            return False # Ne répond pas au port testé
    except:
        return False

# Fonction combinée pour déterminer l'état réel
def etat_reel_machine(ip):
    """Détermine si la machine est en ligne ou pas"""
    ping_result = ping_host(ip)
    
    if ping_result == "En ligne":
        return "En ligne"
    elif ping_result in ["Timeout", "Hôte inaccessible", "Hôte introuvable", "Hors ligne"]:
        return "Hors ligne"
    else:
        return ping_result  # Conserver les erreurs spécifiques

# Détecter les processus et services en cours d'exécution
def detecter_processus(ip):
    try:
        # Scanner les ports communs pour détecter les services
        services_communs = {
            21: "FTP",
            22: "SSH", 
            23: "Telnet",
            25: "SMTP",
            53: "DNS",
            80: "HTTP",
            110: "POP3",
            143: "IMAP",
            443: "HTTPS",
            993: "IMAPS",
            995: "POPS",
            3306: "MySQL",
            5432: "PostgreSQL",
            6379: "Redis",
            8080: "Proxy/Web",
            8443: "HTTPS Alt"
        }
        
        services_actifs = []
        
        for port, service in services_communs.items():
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((ip, port))
            if result == 0:
                services_actifs.append(f"{service} (port {port})")
            sock.close()
        return services_actifs if services_actifs else ["Aucun service détecté"]
        
    except Exception as e:
        return [f"Erreur de détection: {str(e)[:30]}"]

def get_system_info():
    try:
        # Informations système sur la machine locale
        info = {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_usage': psutil.disk_usage('/').percent,
            'boot_time': datetime.fromtimestamp(psutil.boot_time()).strftime('%Y-%m-%d %H:%M:%S'),
            'network_connections': len(psutil.net_connections()),
            'process_count': len(psutil.pids()),
            'cpu_count': psutil.cpu_count(),
            'memory_total': round(psutil.virtual_memory().total / (1024**3), 2),  # GB
            'memory_used': round(psutil.virtual_memory().used / (1024**3), 2),   # GB
            'disk_total': round(psutil.disk_usage('/').total / (1024**3), 2),  # GB
            'disk_used': round(psutil.disk_usage('/').used / (1024**3), 2),     # GB
        }
        return info
    except:
        return None

# Envoyer un message via différents protocoles
def envoyer_message(ip, message, methode='tcp'):
    try:
        if methode == 'tcp':
            return envoyer_message_tcp(ip, message)
        elif methode == 'udp':
            return envoyer_message_udp(ip, message)
        elif methode == 'http':
            return envoyer_message_http(ip, message)
        else:
            return "Méthode non supportée"
    except Exception as e:
        return f"Erreur d'envoi: {str(e)}"

def envoyer_message_tcp(ip, message, port=12345):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((ip, port))
        if result == 0:
            sock.send(message.encode('utf-8'))
            sock.close()
            return f"Message TCP envoyé à {ip}:{port}"
        else:
            return f"Port {port} fermé sur {ip}"
    except Exception as e:
        return f"Erreur TCP: {str(e)}"

def envoyer_message_udp(ip, message, port=12345):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(5)
        sock.sendto(message.encode('utf-8'), (ip, port))
        sock.close()
        return f"Message UDP envoyé à {ip}:{port}"
    except Exception as e:
        return f"Erreur UDP: {str(e)}"

def envoyer_message_http(ip, message, port=80):
    try:
        url = f"http://{ip}:{port}/message"
        data = {'message': message, 'timestamp': datetime.now().isoformat()}
        response = requests.post(url, data=data, timeout=5)
        if response.status_code == 200:
            return f"Message HTTP envoyé à {ip}"
        else:
            return f"Erreur HTTP: {response.status_code}"
    except requests.exceptions.Timeout:
        return "Timeout HTTP"
    except requests.exceptions.ConnectionError:
        return f"Connexion HTTP refusée sur {ip}:{port}"
    except Exception as e:
        return f"Erreur HTTP: {str(e)}"

@app.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM machines")
    machines = cursor.fetchall()

    # Mettre à jour le statut et la durée
    for machine in machines:
        status = etat_reel_machine(machine['ip'])
        
        # Détecter les services si la machine est en ligne
        services = []
        if 'En ligne' in status:
            services = detecter_processus(machine['ip'])
        
        # Récupérer les informations système si c'est la machine locale
        info_systeme = None
        if machine['ip'] in ['127.0.0.1', 'localhost']:
            info_systeme = get_system_info()
            if info_systeme:
                info_str = f"CPU: {info_systeme['cpu_percent']:.1f}% ({info_systeme['cpu_count']} cœurs), RAM: {info_systeme['memory_percent']:.1f}% ({info_systeme['memory_used']}/{info_systeme['memory_total']}GB), Disque: {info_systeme['disk_usage']:.1f}% ({info_systeme['disk_used']}/{info_systeme['disk_total']}GB), Processus: {info_systeme['process_count']}, Connexions: {info_systeme['network_connections']}"
            else:
                info_str = "Informations non disponibles"
        else:
            info_str = "Non applicable (machine distante)"
        
        # Vérifier si le statut a changé
        ancien_statut = machine['statut']
        if ancien_statut != status:
            maintenant = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            services_str = ', '.join(services) if services else 'Aucun'
            cursor.execute("""
                UPDATE machines SET statut=?, dernier_changement=?, services_actifs=?, info_systeme=? WHERE id=?
            """, (status, maintenant, services_str, info_str, machine['id']))
        else:
            # Mettre à jour la durée et les services
            if machine['dernier_changement']:
                duree = calculer_duree(machine['dernier_changement'])
                services_str = ', '.join(services) if services else 'Aucun'
                cursor.execute("""
                    UPDATE machines SET duree_statut=?, services_actifs=?, info_systeme=? WHERE id=?
                """, (duree, services_str, info_str, machine['id']))
    
    conn.commit()

    cursor.execute("SELECT * FROM machines")
    machines = cursor.fetchall()

    return render_template("index.html", machines=machines)

@app.route('/classic')
def classic():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM machines")
    machines = cursor.fetchall()

    # Mettre à jour le statut et la durée
    for machine in machines:
        status = etat_reel_machine(machine['ip'])
        
        # Détecter les services si la machine est en ligne
        services = []
        if 'En ligne' in status:
            services = detecter_processus(machine['ip'])
        
        # Récupérer les informations système si c'est la machine locale
        info_systeme = None
        if machine['ip'] in ['127.0.0.1', 'localhost']:
            info_systeme = get_system_info()
            if info_systeme:
                info_str = f"CPU: {info_systeme['cpu_percent']:.1f}% ({info_systeme['cpu_count']} cœurs), RAM: {info_systeme['memory_percent']:.1f}% ({info_systeme['memory_used']}/{info_systeme['memory_total']}GB), Disque: {info_systeme['disk_usage']:.1f}% ({info_systeme['disk_used']}/{info_systeme['disk_total']}GB), Processus: {info_systeme['process_count']}, Connexions: {info_systeme['network_connections']}"
            else:
                info_str = "Informations non disponibles"
        else:
            info_str = "Non applicable (machine distante)"
        
        # Vérifier si le statut a changé
        ancien_statut = machine['statut']
        if ancien_statut != status:
            maintenant = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            services_str = ', '.join(services) if services else 'Aucun'
            cursor.execute("""
                UPDATE machines SET statut=?, dernier_changement=?, services_actifs=?, info_systeme=? WHERE id=?
            """, (status, maintenant, services_str, info_str, machine['id']))
        else:
            # Mettre à jour la durée et les services
            if machine['dernier_changement']:
                duree = calculer_duree(machine['dernier_changement'])
                services_str = ', '.join(services) if services else 'Aucun'
                cursor.execute("""
                    UPDATE machines SET duree_statut=?, services_actifs=?, info_systeme=? WHERE id=?
                """, (duree, services_str, info_str, machine['id']))
    
    conn.commit()

    cursor.execute("SELECT * FROM machines")
    machines = cursor.fetchall()

    return render_template("index.html", machines=machines)

@app.route('/add', methods=['POST'])
def add():
    name = request.form['name'].strip()
    ip = request.form['ip'].strip()
    
    # Validation des entrées
    if not name:
        flash(' Le nom de la machine ne peut pas être vide', 'error')
        return redirect('/')
    
    if not ip:
        flash(' L\'adresse IP ne peut pas être vide', 'error')
        return redirect('/')
    
    if not valider_ip(ip):
        flash(f' L\'adresse IP "{ip}" n\'est pas valide', 'error')
        return redirect('/')
    
    try:
        # Vérifier si la machine existe déjà
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM machines WHERE ip = ?", (ip,))
        if cursor.fetchone():
            flash(f' Une machine avec l\'IP {ip} existe déjà', 'warning')
            conn.close()
            return redirect('/')
        
        # Test de connectivité
        test_result = etat_reel_machine(ip)
        if test_result in ["IP invalide", "Hôte introuvable", "Hôte inaccessible"]:
            flash(f' Erreur de connexion à {ip}: {test_result}', 'error')
            conn.close()
            return redirect('/')
        
        # Ajouter la machine
        maintenant = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute("INSERT INTO machines (nom, ip, statut, dernier_changement, duree_statut) VALUES (?, ?, ?, ?, ?)", 
                      (name, ip, test_result, maintenant, "0 min"))
        conn.commit()
        
        # Message de succès
        if test_result == "En ligne":
            flash(f' Machine "{name}" ({ip}) ajoutée avec succès - En ligne', 'success')
        else:
            flash(f' Machine "{name}" ({ip}) ajoutée - {test_result}', 'warning')
        
    except sqlite3.Error as e:
        flash(f' Erreur de base de données: {str(e)}', 'error')
    except Exception as e:
        flash(f' Erreur inattendue: {str(e)}', 'error')
    finally:
        try:
            conn.close()
        except:
            pass
    
    return redirect('/')

@app.route('/delete/<int:machine_id>', methods=['POST'])
def delete_machine(machine_id):
    conn = None
    try:
        # Vérifier si la machine existe
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT nom, ip FROM machines WHERE id = ?", (machine_id,))
        machine = cursor.fetchone()
        
        if not machine:
            flash('❌ Machine introuvable', 'error')
            return redirect('/')
        
        # Supprimer les messages associés (avec transaction)
        cursor.execute("DELETE FROM messages_envoyes WHERE machine_id = ?", (machine_id,))
        
        # Supprimer la machine
        cursor.execute("DELETE FROM machines WHERE id = ?", (machine_id,))
        
        # Commit de la transaction
        conn.commit()
        
        flash(f'✅ Machine "{machine["nom"]}" ({machine["ip"]}) supprimée avec succès', 'success')
        
    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        flash(f'❌ Erreur de base de données: {str(e)}', 'error')
    except Exception as e:
        if conn:
            conn.rollback()
        flash(f'❌ Erreur inattendue: {str(e)}', 'error')
    finally:
        if conn:
            conn.close()
    
    return redirect('/')

@app.route('/send_message/<int:machine_id>', methods=['POST'])
def send_message(machine_id):
    message = request.form.get('message', '').strip()
    methode = request.form.get('methode', 'tcp')
    port = request.form.get('port', '12345')
    
    if not message:
        flash('❌ Le message ne peut pas être vide', 'error')
        return redirect('/')
    
    # Récupérer les informations de la machine
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM machines WHERE id = ?", (machine_id,))
    machine = cursor.fetchone()
    
    if not machine:
        flash('❌ Machine non trouvée', 'error')
        return redirect('/')
    
    # Vérifier si la machine est en ligne
    if machine['statut'] != 'En ligne':
        flash(f'⚠️ Impossible d\'envoyer un message : {machine["nom"]} ({machine["ip"]}) n\'est pas en ligne', 'warning')
        return redirect('/')
    
    # Envoyer le message
    try:
        port = int(port)
    except ValueError:
        port = 12345
    
    result = envoyer_message(machine['ip'], message, methode)
    
    # Enregistrer le message dans la base de données
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    statut_envoi = "Succès" if "envoyé" in result.lower() else "Échec"
    
    try:
        port = int(port)
    except ValueError:
        port = 12345
    
    cursor.execute("""
        INSERT INTO messages_envoyes 
        (machine_id, machine_nom, machine_ip, message, methode, port, timestamp, statut) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (machine_id, machine['nom'], machine['ip'], message, methode, port, timestamp, statut_envoi))
    conn.commit()
    
    if "envoyé" in result.lower():
        flash(f'✅ {result} à {machine["nom"]} ({machine["ip"]})', 'success')
    else:
        flash(f'❌ {result}', 'error')
    
    return redirect('/')

@app.route('/messages')
def messages():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT me.*, m.nom as machine_nom, m.ip as machine_ip 
        FROM messages_envoyes me 
        LEFT JOIN machines m ON me.machine_id = m.id 
        ORDER BY me.timestamp DESC
    """)
    messages = cursor.fetchall()
    return render_template("messages.html", messages=messages)

@app.route('/delete/<int:machine_id>', methods=['POST'])
def delete(machine_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM machines WHERE id = ?", (machine_id,))
    conn.commit()

    return redirect('/')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
