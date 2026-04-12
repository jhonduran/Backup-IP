from netmiko import ConnectHandler
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

SWITCH_PASSWORD = os.getenv("SWITCH_PASSWORD")
if not SWITCH_PASSWORD:
    raise ValueError("❌ No se encontró SWITCH_PASSWORD en el archivo .env")

# ====================== CONFIGURACIÓN ======================
devices = [
    {
        'device_type': 'hp_comware_telnet',
        'host': '192.168.250.5',
        'username': 'admin',
        'password': SWITCH_PASSWORD,
        'name': 'HP_Switch_5'
    },
    {
        'device_type': 'hp_comware_telnet',
        'host': '192.168.250.6',
        'username': 'admin',
        'password': SWITCH_PASSWORD,
        'name': 'HP_Switch_6'
    },
    {
        'device_type': 'dell_powerconnect_telnet',
        'host': '192.168.4.10',
        'username': 'admin',
        'password': SWITCH_PASSWORD,
        'secret': SWITCH_PASSWORD,
        'name': 'PLANTA_ALCOHOL_1'
    },
    {
        'device_type': 'dell_powerconnect_telnet',
        'host': '192.168.4.11',
        'username': 'admin',
        'password': SWITCH_PASSWORD,
        'secret': SWITCH_PASSWORD,
        'name': 'PLANTA_ALCOHOL_2'
    },
]

BASE_PATH = r"C:\Users\john2\OneDrive\EmpresaBackups"

# ====================== FILTRO DE FECHA ======================
hoy = datetime.now()
dia = hoy.day

# Solo ejecutar backups los días 15 y 28 de cada mes
if dia not in [15, 29]:
    print(f" Hoy es día {dia}. Los backups solo se ejecutan los días 15 y 28.")
    print("   Script finalizado sin ejecutar backups.")
    exit()   # Termina el script sin hacer nada

print(f"🚀 Iniciando backups automáticos - Día {dia} del mes")

success_count = 0
error_count = 0

for device in devices:
    device_name = device.get('name', device['host'])
    ip = device['host']

    try:
        print(f"\n🔌 Conectando a {device_name} ({ip})...")

        conn_dict = {k: v for k, v in device.items() if k != 'name'}

        net_connect = ConnectHandler(
            **conn_dict,
            timeout=45,
            conn_timeout=40,
            global_delay_factor=3,
            fast_cli=False
        )

        print("✅ Conectado!")

        if 'secret' in device:
            net_connect.enable()
            print("🔓 Modo enable activado")

        command = "display current-configuration" if device['device_type'] == 'hp_comware_telnet' else "show running-config"
        output = net_connect.send_command(command, read_timeout=90)

        # ==================== CARPETA POR IP ====================
        fecha_carpeta = hoy.strftime("%Y-%m")          # Ej: 2026-03
        carpeta_ip = os.path.join(BASE_PATH, fecha_carpeta, ip)
        os.makedirs(carpeta_ip, exist_ok=True)

        # Nombre del archivo
        now = datetime.now()
        filename = f"{device_name}_{ip}_{now.strftime('%Y%m%d_%H%M')}.txt"
        filepath = os.path.join(carpeta_ip, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(output)

        print(f"📁 Backup guardado → {filepath}")
        success_count += 1
        net_connect.disconnect()

    except Exception as e:
        print(f"❌ Error en {device_name} ({ip}): {e}")
        error_count += 1

# ====================== RESUMEN ======================
print("\n" + "="*90)
print("🏁 RESUMEN FINAL DE BACKUPS AUTOMÁTICOS")
print("="*90)
print(f"✅ Éxitos   : {success_count}")
print(f"❌ Errores  : {error_count}")
print(f"📂 Carpeta principal : {BASE_PATH}")
print(f"📅 Fecha ejecutada   : {hoy.strftime('%Y-%m-%d')}")
print("="*90)