# port_test.py
import socket

ip = ""  # ← TU IP DE LA VM
port = 389

print(f"Probando conexión a {ip}:{port}...\n")

try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    result = sock.connect_ex((ip, port))
    sock.close()

    if result == 0:
        print("PUERTO 389 ABIERTO")
        print("→ LDAP está escuchando en la VM")
    else:
        print("PUERTO 389 CERRADO")
        print("→ Posibles causas:")
        print("   - Firewall bloquea el puerto")
        print("   - Servicio AD no está corriendo")
        print("   - IP incorrecta")
except Exception as e:
    print("Error:", e)