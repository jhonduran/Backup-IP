from datetime import datetime
from dotenv import load_dotenv
import os
import paramiko
import time
from netmiko import ConnectHandler

load_dotenv()

SWITCH_PASSWORD = os.getenv("SWITCH_PASSWORD")
if not SWITCH_PASSWORD:
    raise ValueError(" No se encontró SWITCH_PASSWORD en el archivo .env")

print("Contraseña cargada correctamente desde .env\n")

# ====================== DISPOSITIVOS ======================
devices = [
    {
        'name': 'HP_Switch_5',
        'host': '192.168.250.5',
        'device_type': 'hp_comware_telnet',
        'use_netmiko': True
    },
    {
        'name': 'HP_Switch_6',
        'host': '192.168.250.6',
        'device_type': 'hp_comware_telnet',
        'use_netmiko': True
    },
    {
        'name': 'PLANTA_ALCOHOL_1',
        'host': '192.168.4.10',
        'device_type': 'dell_powerconnect_telnet',
        'secret': SWITCH_PASSWORD,      # ← Importante para Dell
        'use_netmiko': True
    },
    {
        'name': 'PLANTA_ALCOHOL_2',
        'host': '192.168.4.11',
        'device_type': 'dell_powerconnect_telnet',
        'secret': SWITCH_PASSWORD,      # ← Importante para Dell
        'use_netmiko': True
    },
    # Switch especial que necesita Paramiko
    {
        'name': 'Switch_10.2.0.15',
        'host': '10.2.0.15',
        'port': 1030,
        'use_netmiko': False
    },
   {
        'name': 'Switch_10.2.0.12',
        'host': '10.2.0.12',
        'port': 22,
        'use_netmiko': False
    },
   {
    'device_type': 'cisco_ios_telnet',      # ← Más tolerante que dell_powerconnect_telnet
    'host': '10.2.0.11',
    'username': 'admin',
    'password': SWITCH_PASSWORD,
    'name': 'Switch_10.2.0.11'
    },
   {
        'name': 'Switch_192.9.204.66',
        'host': '192.9.204.66',
        'port': 1030,
        'use_netmiko': False
    },

    {"name": "Switch_192.9.204.68",
     "host": "192.9.204.68",
     "port": 1030,
     "use_netmiko": False
     },
]


BASE_PATH = r"C:\Users\pract3.sistemas\OneDrive\EmpresaBackups"
os.makedirs(BASE_PATH, exist_ok=True)

print("Iniciando backups automáticos...\n")

success_count = 0
error_count = 0

for dev in devices:
    name = dev['name']
    ip = dev['host']

    try:
        print(f" Conectando a {name} ({ip})...")

        if dev.get('use_netmiko', True):
            # ====================== NETMIKO ======================
            conn_params = {
                'device_type': dev['device_type'],
                'host': ip,
                'username': 'admin',
                'password': SWITCH_PASSWORD,
            }
            if 'secret' in dev:
                conn_params['secret'] = dev['secret']

            net_connect = ConnectHandler(
                **conn_params,
                timeout=90,
                conn_timeout=60,
                global_delay_factor=4,
                fast_cli=False
            )

            # Solo entrar en enable si se definió secret
            if 'secret' in dev:
                net_connect.enable()
                print("Modo enable activado")

            command = "display current-configuration" if 'hp_comware' in dev['device_type'] else "show running-config"
            output = net_connect.send_command(command, read_timeout=120)
            net_connect.disconnect()

        else:
            # ====================== PARAMIKO para el switch 10.2.0.15 ======================
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            ssh.connect(
                ip,
                port=dev['port'],
                username='admin',
                password=SWITCH_PASSWORD,
                timeout=45,
                look_for_keys=False,
                allow_agent=False
            )

            channel = ssh.invoke_shell()
            time.sleep(4)
            channel.send("show running-config\n")
            time.sleep(10)

            output = ""
            start = time.time()
            while time.time() - start < 15:
                if channel.recv_ready():
                    output += channel.recv(8192).decode('utf-8', errors='ignore')
                time.sleep(0.5)

            ssh.close()

        # ====================== GUARDAR BACKUP ======================
        now = datetime.now()
        fecha_carpeta = now.strftime("%Y-%m")
        carpeta_ip = os.path.join(BASE_PATH, fecha_carpeta, ip)
        os.makedirs(carpeta_ip, exist_ok=True)

        filename = f"{name}_{ip}_{now.strftime('%Y%m%d_%H%M')}.txt"
        filepath = os.path.join(carpeta_ip, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(output)

        print(f" Backup guardado → {filepath}")
        success_count += 1

    except Exception as e:
        print(f" Error en {name}: {e}")
        error_count += 1

# ====================== RESUMEN ======================
print("\n" + "="*90)
print(" RESUMEN FINAL")
print("="*90)
print(f" Éxitos   : {success_count}")
print(f" Errores  : {error_count}")
print(f" Carpeta  : {BASE_PATH}")
print("="*90)