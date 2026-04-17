import subprocess
import time
import sys
import os
import socket

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def kill_port_owner(port):
    try:
        output = subprocess.check_output(f"netstat -ano | findstr :{port}", shell=True).decode()
        for line in output.strip().split('\n'):
            if 'LISTENING' in line:
                pid = line.strip().split()[-1]
                print(f"[*] Cleaning up port {port} (PID: {pid})...")
                subprocess.run(f"taskkill /F /PID {pid}", shell=True, capture_output=True)
    except Exception: pass

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    print("[*] CinemaMind Full Stack Starting...")
    for port in [8080, 5000]:
        if is_port_in_use(port): kill_port_owner(port)
    
    print("[*] Starting Vector DB (8080)...")
    mock_p = subprocess.Popen([sys.executable, os.path.join(script_dir, "mock_endee.py")])
    time.sleep(2)
    
    print("[*] Starting Web Interface (5000)...")
    app_p = subprocess.Popen([sys.executable, os.path.join(script_dir, "app.py")])
    
    print("\n------------------------------------------------")
    print("SUCCESS: CinemaMind is running!")
    print("WEB UI: http://localhost:5000")
    print("------------------------------------------------\n")
    try:
        while True: time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down...")
        mock_p.terminate()
        app_p.terminate()

if __name__ == "__main__": main()
