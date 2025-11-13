#!/usr/bin/env python
import os
import django
from decouple import config
from django.contrib.auth import authenticate
from ldap3 import Server, Connection, ALL

# CONFIGURAR DJANGO
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tp3_crud.settings')  # ← CAMBIA AQUÍ
django.setup()

print("PROBANDO CONEXIÓN LDAP con ldap3...\n")

# === PRUEBA DE CONEXIÓN ===
try:
    server = Server(
        host=config('LDAP_AUTH_URL').replace('ldap://', ''),  
        port=389,
        use_ssl=False,
        get_info=ALL
    )
    
    conn = Connection(
        server=server,
        user=config('LDAP_AUTH_CONNECTION_USERNAME'),
        password=config('LDAP_AUTH_CONNECTION_PASSWORD'),
        auto_bind=True,
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
    exit(1)  # Salir si falla el bind

print("\n" + "="*60)
print("PROBANDO LOGIN DE USUARIO...\n")

# === PRUEBA DE LOGIN ===
user = authenticate(username="SILVIA.TAPIA", password="Test123!")
if user:
    print(f"LOGIN EXITOSO!")
    print(f"  Usuario: {user.username}")
    print(f"  Nombre: {user.first_name} {user.last_name}")
    print(f"  Email: {user.email}")
else:
    print("FALLO EN LOGIN")
    print("Posibles causas:")
    print("  - Contraseña incorrecta")
    print("  - Usuario no en grupo GG_Gerencia")
    print("  - Filtro de búsqueda mal configurado")

print("\n" + "="*60)
print("PROBANDO BÚSQUEDA CON ldap3 PURO...\n")

# === PRUEBA DE BÚSQUEDA ===
try:
    LDAP_URL = "ldap://192.168.1.53:389"
    BIND_DN = "CN=ldap_service,CN=Users,DC=IFTS,DC=local"
    BIND_PW = "BindPass123"
    SEARCH_BASE = "DC=IFTS,DC=local"
    USERNAME = "pruebaldap"  # ← AQUÍ VA EL sAMAccountName REAL
    FILTER = f"(sAMAccountName={USERNAME})"

    print(f"Buscando: {USERNAME}")
    print(f"Filtro: {FILTER}\n")

    server = Server(LDAP_URL, get_info=ALL)
    conn = Connection(
        server,
        user=BIND_DN,
        password=BIND_PW,
        auto_bind=True
    )
    print("BIND OK CON ldap_service\n")

    conn.search(
        search_base=SEARCH_BASE,
        search_filter=FILTER,
        attributes=['sAMAccountName', 'givenName', 'sn', 'mail', 'memberOf']
    )

    if conn.entries:
        print("USUARIO ENCONTRADO:")
        for entry in conn.entries:
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
        print("  - sAMAccountName incorrecto (verifica en dsa.msc → pestaña Cuenta)")
        print("  - Usuario no existe")
        print("  - No está en DC=IFTS,DC=local")

    conn.unbind()

except Exception as e:
    print(f"ERROR EN BÚSQUEDA: {e}")