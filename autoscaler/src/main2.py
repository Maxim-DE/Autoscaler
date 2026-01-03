#!/usr/bin/env python3
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
import sys
from datetime import datetime
import os

# Путь к файлу логов (рядом со скриптом)
LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'log.txt')

def log_to_file(message):
    """Запись сообщения в файл логов"""
    try:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(f"[{timestamp}] {message}\n")
    except Exception as e:
        print(f"ERROR writing to log file: {e}")

class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # Read data
            length = int(self.headers['Content-Length'])
            data = json.loads(self.rfile.read(length))
            
            # Handle both array and object formats
            alerts = []
            if isinstance(data, list):
                alerts = data
            elif isinstance(data, dict) and 'alerts' in data:
                alerts = data['alerts']
            else:
                alerts = [data]
            
            # Log to console AND file
            log_message = f"Received {len(alerts)} alert(s)"
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] {log_message}")
            log_to_file(f"POST / - {log_message}")
            
            for alert in alerts:
                if isinstance(alert, dict):
                    name = alert.get('labels', {}).get('alertname', 'unknown')
                    severity = alert.get('labels', {}).get('severity', 'unknown')
                    summary = alert.get('annotations', {}).get('summary', '')
                    
                    alert_message = f"[{severity}] {name}: {summary}"
                    print(f"  {alert_message}")
                    log_to_file(f"  {alert_message}")
            
            sys.stdout.flush()
            
            # Response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                'status': 'success',
                'received': len(alerts),
                'timestamp': datetime.now().isoformat()
            }
            self.wfile.write(json.dumps(response).encode())
            
            # Log success
            log_to_file(f"Response sent: 200 OK")
            
        except Exception as e:
            error_msg = f"ERROR: {e}"
            print(f"{error_msg}")
            log_to_file(error_msg)
            sys.stdout.flush()
            self.send_response(500)
            self.end_headers()
            log_to_file(f"Response sent: 500 Internal Server Error")
    
    def do_GET(self):
        client_ip = self.client_address[0]
        log_message = f"GET {self.path} from {client_ip}"
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {log_message}")
        log_to_file(log_message)
        
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'OK')
        
        log_to_file(f"Response sent: 200 OK for GET {self.path}")
    
    def log_message(self, format, *args):
        """Захватываем стандартное логирование и пишем в файл"""
        message = format % args
        log_to_file(f"HTTP: {message}")

if __name__ == '__main__':
    # Создаем/очищаем файл логов при запуске
    try:
        with open(LOG_FILE, 'w', encoding='utf-8') as f:
            f.write(f"=== Webhook Receiver Log Started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n")
            f.write(f"Script: {os.path.basename(__file__)}\n")
            f.write(f"Log file: {LOG_FILE}\n")
            f.write("=" * 60 + "\n")
    except Exception as e:
        print(f"ERROR creating log file: {e}")
    
    print(f"Webhook receiver starting on port 9099...")
    print(f"Log file: {LOG_FILE}")
    log_to_file("Server starting on port 9099")
    
    try:
        server = HTTPServer(('0.0.0.0', 9099), Handler)
        log_to_file("Server started successfully")
        server.serve_forever()
    except KeyboardInterrupt:
        log_to_file("Server stopped by user")
        print("\nServer stopped")
    except Exception as e:
        error_msg = f"Server error: {e}"
        log_to_file(error_msg)
        print(error_msg)