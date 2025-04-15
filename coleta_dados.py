from flask import Flask, request
import sqlite3
from datetime import datetime
import os
from werkzeug.middleware.proxy_fix import ProxyFix


app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1) 
DB_NAME = 'logs.db'

# Cria o banco e a tabela se não existir
def init_db():
    if not os.path.exists(DB_NAME):
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ip TEXT,
                    user_agent TEXT,
                    route TEXT,
                    timestamp TEXT
                )
            ''')
            conn.commit()

# Função para registrar logs no banco
def log_attempt(ip, user_agent, route):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO logs (ip, user_agent, route, timestamp)
            VALUES (?, ?, ?, ?)
        ''', (ip, user_agent, route, timestamp))
        conn.commit()

# Função para exibir os logs do banco de dados
def print_logs():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id, ip, user_agent, route, timestamp FROM logs')
        logs = cursor.fetchall()
        
        print("\n===== LOGS REGISTRADOS =====")
        for log in logs:
            print(f"ID: {log[0]}")
            print(f"IP: {log[1]}")
            print(f"User-Agent: {log[2]}")
            print(f"Rota: {log[3]}")
            print(f"Timestamp: {log[4]}")
            print("-" * 30)

# ✅ Nova rota para receber IP via JavaScript (fetch)
@app.route('/log')
def log_from_js():
    ip = request.args.get('ip', request.remote_addr)
    user_agent = request.headers.get('User-Agent', 'Desconhecido')
    route = '/log (via JS)'
    
    log_attempt(ip, user_agent, route)
    print(f"[JS-LOG] IP: {ip} | Rota: {route} | User-Agent: {user_agent}")
    return "Log registrado com sucesso"

# captura rotas falsas
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    ip = request.headers.get('X-Real-IP') or \
    request.headers.get('X-Forwarded-For', request.remote_addr).split(',')[0].strip()
    user_agent = request.headers.get('User-Agent', 'Desconhecido')
    route = "/" + path

    log_attempt(ip, user_agent, route)
    
    # ✅ Aqui você visualiza o acesso em tempo real no Render
    print(f"[ACESSO] IP: {ip} | Rota: {route} | User-Agent: {user_agent}")
    
    return "404 - Página não encontrada", 404  # Simula página falsa

if __name__ == '__main__':
    init_db()
    print("[INICIANDO SERVIDOR]")
    print_logs()
    app.run(host='0.0.0.0', port=8080)
