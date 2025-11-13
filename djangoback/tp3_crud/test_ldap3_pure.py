#!/usr/bin/env python
"""
Script de prueba para la implementación de ldap3 puro
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tp3_crud.settings')
django.setup()

from apps.juego.ldap_utils import LDAPConnection
from django.contrib.auth import authenticate

print("="*70)
print("PRUEBA DE LDAP3 PURO - IMPLEMENTACIÓN PERSONALIZADA")
print("="*70)
print()

# =============================================================================
# 1. PRUEBA DE CONEXIÓN BÁSICA
# =============================================================================
print("1. PROBANDO CONEXIÓN BÁSICA AL SERVIDOR AD...")
print("-" * 70)

try:
    ldap = LDAPConnection()
    conn = ldap.get_connection()

    if conn:
        print("✓ CONEXIÓN EXITOSA")
        print(f"  Servidor: {ldap.server_url}")
        print(f"  Base DN: {ldap.search_base}")
        print(f"  Bind DN: {ldap.bind_dn}")
        conn.unbind()
    else:
        print("✗ FALLO EN CONEXIÓN")
        print("  Verifica las credenciales y configuración en .env")
except Exception as e:
    print(f"✗ ERROR: {e}")

print()

# =============================================================================
# 2. PRUEBA DE BÚSQUEDA DE USUARIO
# =============================================================================
print("2. PROBANDO BÚSQUEDA DE USUARIO...")
print("-" * 70)

# Cambia este username por uno válido en tu AD
TEST_USERNAME = "pruebaldap"  # <-- CAMBIA ESTO

try:
    ldap = LDAPConnection()
    user_data = ldap.search_user(TEST_USERNAME)

    if user_data:
        print(f"✓ USUARIO ENCONTRADO: {TEST_USERNAME}")
        print(f"  DN: {user_data['dn']}")
        print(f"  Username: {user_data['username']}")
        print(f"  Nombre: {user_data['first_name']} {user_data['last_name']}")
        print(f"  Email: {user_data['email']}")
        print(f"  Grupos: {len(user_data['groups'])}")
        if user_data['groups']:
            print("  Miembro de:")
            for group in user_data['groups'][:5]:  # Mostrar solo los primeros 5
                print(f"    - {group}")
    else:
        print(f"✗ USUARIO NO ENCONTRADO: {TEST_USERNAME}")
        print("  Verifica que el usuario existe en AD")
except Exception as e:
    print(f"✗ ERROR: {e}")

print()

# =============================================================================
# 3. PRUEBA DE AUTENTICACIÓN
# =============================================================================
print("3. PROBANDO AUTENTICACIÓN COMPLETA...")
print("-" * 70)

# Cambia estos valores por credenciales válidas
TEST_USERNAME = "pruebaldap"  # <-- CAMBIA ESTO
TEST_PASSWORD = "Test123!"    # <-- CAMBIA ESTO

try:
    ldap = LDAPConnection()
    user_data = ldap.authenticate_user(TEST_USERNAME, TEST_PASSWORD)

    if user_data:
        print(f"✓ AUTENTICACIÓN EXITOSA para {TEST_USERNAME}")
        print(f"  DN: {user_data['dn']}")
        print(f"  Nombre completo: {user_data['first_name']} {user_data['last_name']}")
        print(f"  Email: {user_data['email']}")
    else:
        print(f"✗ AUTENTICACIÓN FALLIDA para {TEST_USERNAME}")
        print("  Posibles causas:")
        print("    - Contraseña incorrecta")
        print("    - Usuario no existe")
        print("    - Cuenta bloqueada o deshabilitada")
except Exception as e:
    print(f"✗ ERROR: {e}")

print()

# =============================================================================
# 4. PRUEBA CON DJANGO AUTHENTICATE
# =============================================================================
print("4. PROBANDO BACKEND DE DJANGO...")
print("-" * 70)

try:
    user = authenticate(username=TEST_USERNAME, password=TEST_PASSWORD)

    if user:
        print(f"✓ AUTENTICACIÓN DJANGO EXITOSA")
        print(f"  Usuario Django: {user.username}")
        print(f"  ID: {user.id}")
        print(f"  Nombre: {user.first_name} {user.last_name}")
        print(f"  Email: {user.email}")
        print(f"  Es superusuario: {user.is_superuser}")
        print(f"  Es staff: {user.is_staff}")
        print(f"  Usuario creado: {user.date_joined}")
    else:
        print(f"✗ AUTENTICACIÓN DJANGO FALLIDA")
        print("  El backend personalizado no pudo autenticar al usuario")
except Exception as e:
    print(f"✗ ERROR: {e}")

print()
print("="*70)
print("PRUEBAS COMPLETADAS")
print("="*70)
print()
print("NOTAS:")
print("- Si todas las pruebas pasan, la implementación está funcionando correctamente")
print("- Si alguna prueba falla, revisa los logs en la consola")
print("- Verifica que las variables de entorno en .env estén configuradas correctamente")
print("- El logging está activado en settings.py para facilitar el debugging")
print()
