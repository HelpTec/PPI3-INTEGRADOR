# bind_test.py
import os
from decouple import config
import ldap

# Carga .env (mismo que usa Django)
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent
from dotenv import load_dotenv
load_dotenv(BASE_DIR / '.env')

# Configuración
LDAP_URL = config('LDAP_AUTH_URL')
BIND_DN = config('LDAP_AUTH_CONNECTION_USERNAME')
BIND_PW = config('LDAP_AUTH_CONNECTION_PASSWORD')

print(f"Probando bind a {LDAP_URL}")
print(f"Usuario: {BIND_DN}\n")

try:
    # Inicializa conexión
    conn = ldap.initialize(LDAP_URL)
    conn.set_option(ldap.OPT_REFERRALS, 0)
    conn.set_option(ldap.OPT_PROTOCOL_VERSION, 3)
    
    # Intenta bind
    conn.simple_bind_s(BIND_DN, BIND_PW)
    
    print("BIND EXITOSO")
    print("→ El usuario bind funciona perfectamente")
    
    # Cierra
    conn.unbind_s()

except ldap.INVALID_CREDENTIALS:
    print("FALLO: Credenciales inválidas")
    print("→ Contraseña incorrecta o usuario bloqueado")
except ldap.SERVER_DOWN:
    print("FALLO: Servidor no responde")
except ldap.LDAPError as e:
    print(f"FALLO LDAP: {e}")
except Exception as e:
    print(f"Error inesperado: {e}")