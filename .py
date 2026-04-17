import paramiko
import time
from datetime import datetime
import os
from dotenv import load_dotenv   # ← Importante para leer el .env

# ====================== CARGAR .env ======================
load_dotenv()

SWITCH_PASSWORD = os.getenv("SWITCH_PASSWORD")
if not SWITCH_PASSWORD:
    raise ValueError("❌ No se encontró SWITCH_PASSWORD en el archivo .env")

print("✅ Contraseña cargada correctamente desde .env\n")

# ====================== CONFIGURACIÓN DEL SWITCH ======================
HOST = '10.2.0.15'
PORT = 1030
USERNAME = 'admin'
PASSWORD = SWITCH_PASSWORD

# ====================== CONEXIÓN CON PARAMIKO ======================
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    print(f"🔌 Conectando vía SSH a {HOST}:{PORT}...")

    ssh.connect(
        HOST,
        port=PORT,
        username=USERNAME,
        password=PASSWORD,
        timeout=45,
        look_for_keys=False,
        allow_agent=False,
        auth_timeout=30
    )

    print("✅ Conexión SSH establecida!")

    # Canal interactivo
    channel = ssh.invoke_shell()
    time.sleep(4)

    # Enviar comando
    print("📤 Enviando 'show running-config'...")
    channel.send("show running-config\n")
    time.sleep(10)

    # Leer la salida
    output = ""
    timeout = 15
    start_time = time.time()

    while time.time() - start_time < timeout:
        if channel.recv_ready():
            data = channel.recv(8192).decode('utf-8', errors='ignore')
            output += data
            time.sleep(0.5)
        else:
            time.sleep(1)

    print(f"✅ Comando ejecutado. Longitud de salida: {len(output)} caracteres")

    if len(output) < 100:
        print("⚠️ Advertencia: La salida parece muy corta.")

    # Guardar backup
    now = datetime.now()
    filename = f"Switch_10.2.0.15_{now.strftime('%Y%m%d_%H%M')}.txt"
    filepath = os.path.join(r"C:\Users\pract3.sistemas\OneDrive\EmpresaBackups", filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(output)

    print(f"✅ Backup guardado correctamente en:\n   {filepath}")

except Exception as e:
    print(f"❌ Error durante la conexión o ejecución: {e}")

finally:
    ssh.close()
    print("🔌 Conexión cerrada.")

print("\nPrueba finalizada.")