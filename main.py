from netmiko import ConnectHandler
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

device = {
    'device_type': 'hp_comware_telnet',
    'host': '192.168.250.5',
    'username': 'admin',
    'password': os.getenv("SWITCH_PASSWORD")
}

try:
    print("Conectando...")

    connection = ConnectHandler(**device)

    print("Conectado!")

    output = connection.send_command("display current-configuration")

    filename = f"backup_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"

    filepath = r"C:\Users\john2\OneDrive\EmpresaBackups\\" + filename

    with open(filepath, "w") as f:
        f.write(output)

    print("✅ Backup guardado en OneDrive:", filepath)

    connection.disconnect()

except Exception as e:
    print("❌ Error:", e)
