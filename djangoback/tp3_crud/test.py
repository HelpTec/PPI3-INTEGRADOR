#!/usr/bin/env python
import os
import django
from decouple import config

# Configura Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tp3_crud.settings')  # ← CAMBIA AQUÍ
django.setup()

from django.contrib.auth import authenticate
from django_python3_ldap.ldap import connection
from ldap3 import Server, Connection, ALL, SUBTREE

print("PROBANDO CONEXIÓN LDAP con ldap3...\n")

# === PRUEBA DE CONEXIÓN ===
try:
    server = Server(
        host=config('LDAP_AUTH_URL').replace('ldap://', ''),  
        port=389,
        use_ssl=False  # Cambia a True si usas LDAPS
    )
    
    conn = Connection(
        server=server,
        user=config('LDAP_AUTH_CONNECTION_USERNAME'),
        password=config('LDAP_AUTH_CONNECTION_PASSWORD'),
        auto_bind=True,
        client_strategy='SYNC',
        receive_timeout=10
    )
    
    print("CONEXIÓN EXITOSA al servidor AD!")
    print(f"  URL: {config('LDAP_AUTH_URL')}")
    print(f"  Bind DN: {config('LDAP_AUTH_CONNECTION_USERNAME')}")
    
    

except Exception as e:
    print(f"FALLO EN CONEXIÓN: {e}")
    print("Posibles causas:")
    print("  - IP incorrecta o puerto 389 bloqueado")
    print("  - Usuario bind o contraseña incorrectos")
    print("  - Firewall en la VM")

print("\n" + "="*60)
print("PROBANDO LOGIN DE USUARIO...\n")

# === PRUEBA DE LOGIN ===
user = authenticate(username="pruebaldap", password="Test123!")
print(user)
if user:
    print(f"LOGIN EXITOSO!")
    print(f"  Usuario: {user.username}")
    print(f"  Nombre: {user.first_name} {user.last_name}")
    print(f"  Email: {user.email}")
else:
    print("FALLO EN LOGIN")
    print("Posibles causas:")
    print("  - Contraseña incorrecta")
    print("  - Usuario no en grupo DjangoUsers")
    print("  - Filtro de búsqueda mal configurado")
conn.unbind()
# ==PRUEBA DE BUSQUEDA==
#!/usr/bin/env python
import ldap3

# === CONFIGURACIÓN ===
LDAP_URL = "ldap://"
BIND_DN = ""
BIND_PW = ""

SEARCH_BASE = ""
USERNAME = ""
FILTER = f"(sAMAccountName={USERNAME})"

print("PROBANDO BÚSQUEDA CON ldap3 PURO (CORREGIDO)...\n")

try:
    # CONECTAR
    server = ldap3.Server(LDAP_URL, get_info=ldap3.ALL)
    conn = ldap3.Connection(
        server,
        user=BIND_DN,
        password=BIND_PW,
        auto_bind=True
    )
    print("BIND OK CON ldap_service\n")

    # BÚSQUEDA → SIN 'dn'
    conn.search(
        search_base=SEARCH_BASE,
        search_filter=FILTER,
        attributes=['sAMAccountName', 'givenName', 'sn', 'mail', 'memberOf']
    )

    if conn.entries:
        print("USUARIO ENCONTRADO:")
        for entry in conn.entries:
            # DN viene en entry.entry_dn
            print(f"  DN: {entry.entry_dn}")
            print(f"  Username: {entry.sAMAccountName.value}")
            print(f"  Nombre: {entry.givenName.value if entry.givenName else 'N/A'}")
            print(f"  Apellido: {entry.sn.value if entry.sn else 'N/A'}")
            print(f"  Email: {entry.mail.value if entry.mail else 'N/A'}")
            print(f"  Grupos: {len(entry.memberOf) if entry.memberOf else 0}")
            if entry.memberOf:
                for g in entry.memberOf:
                    print(f"    → {g}")
    else:
        print("NO SE ENCONTRÓ EL USUARIO")
        print("Posibles causas:")
        print("  - sAMAccountName incorrecto")
        print("  - Usuario no existe")
        print("  - Filtro mal escrito")

    conn.unbind()

except Exception as e:
    print(f"ERROR: {e}")