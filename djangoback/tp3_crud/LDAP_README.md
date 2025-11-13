# Implementación de LDAP con ldap3 Puro

Esta implementación reemplaza `django-python3-ldap` con una solución personalizada usando `ldap3` puro.

## Archivos Creados

### 1. `apps/juego/ldap_utils.py`
Utilidades para trabajar con LDAP:
- `LDAPConnection`: Clase para manejar conexiones LDAP
- `get_connection()`: Crea conexiones LDAP
- `search_user()`: Busca usuarios en Active Directory
- `authenticate_user()`: Autentica usuarios contra AD

### 2. `apps/juego/ldap_backend.py`
Backend de autenticación personalizado:
- `LDAP3Backend`: Backend de autenticación que implementa `BaseBackend` de Django
- Autentica usuarios contra AD
- Crea/actualiza usuarios de Django automáticamente

### 3. `requirements.txt`
Dependencias necesarias (simplificadas):
- Django 4.2.17
- ldap3 >= 2.9.1
- python-decouple
- python-dotenv
- django-bootstrap5

## Configuración

### Variables de Entorno (.env)

Asegúrate de tener estas variables configuradas en tu archivo `.env`:

```env
# Servidor LDAP
LDAP_AUTH_URL=ldap://192.168.x.x

# Usar TLS/SSL (True o False)
LDAP_AUTH_USE_TLS=False

# Usuario bind (con permisos de lectura en AD)
LDAP_AUTH_CONNECTION_USERNAME=CN=ldap_service,CN=Users,DC=IFTS,DC=local
LDAP_AUTH_CONNECTION_PASSWORD=tu_password_aqui

# Base DN donde buscar usuarios
LDAP_AUTH_SEARCH_BASE=DC=IFTS,DC=local
```

### Cambios en settings.py

La configuración ya fue actualizada:
- Removido `django_python3_ldap` de `INSTALLED_APPS`
- Backend de autenticación cambiado a `apps.juego.ldap_backend.LDAP3Backend`
- Configuración simplificada de LDAP
- Logging activado para debugging

## Instalación

1. Desinstalar paquete anterior (si existe):
```bash
pip uninstall django-python3-ldap
```

2. Instalar dependencias:
```bash
pip install -r requirements.txt
```

3. Verificar variables de entorno en `.env`

## Pruebas

### Prueba rápida con el script de test:
```bash
python test_ldap3_pure.py
```

Este script prueba:
1. Conexión básica al servidor AD
2. Búsqueda de usuario
3. Autenticación con ldap3
4. Autenticación con el backend de Django

### Prueba desde la aplicación:
1. Ejecutar el servidor Django:
```bash
python manage.py runserver
```

2. Ir a la página de login
3. Ingresar credenciales de AD
4. El backend intentará autenticar contra AD automáticamente

## Ventajas de esta Implementación

1. **Control Total**: Tienes acceso completo al código LDAP
2. **Sin Dependencias Innecesarias**: Solo usas ldap3, sin capas adicionales
3. **Fácil Debugging**: Logs claros y código simple de entender
4. **Flexible**: Puedes extender fácilmente la funcionalidad
5. **Mantenible**: Código claro y bien documentado

## Cómo Funciona

### Flujo de Autenticación:

1. Usuario ingresa username y password en el formulario de login
2. Vista `LoginAuth` llama a `authenticate(username, password)`
3. Django usa el `LDAP3Backend` configurado
4. El backend:
   - Usa `LDAPConnection` para buscar el usuario en AD por `sAMAccountName`
   - Obtiene el DN del usuario
   - Intenta hacer bind con el DN y password del usuario
   - Si el bind es exitoso, autentica al usuario
   - Crea o actualiza el usuario en la base de datos de Django
   - Retorna el objeto User de Django
5. La vista hace login del usuario y lo redirige a home

## Personalización

### Agregar más campos de AD:

En `ldap_utils.py`, método `search_user()`, agrega más atributos:

```python
attributes=[
    'sAMAccountName',
    'givenName',
    'sn',
    'mail',
    'memberOf',
    'distinguishedName',
    'telephoneNumber',  # <-- Nuevo campo
    'department',       # <-- Nuevo campo
]
```

### Filtrar por grupo:

En `ldap_backend.py`, método `authenticate()`, agrega validación:

```python
# Verificar que el usuario pertenece a un grupo específico
required_group = "CN=DjangoUsers,CN=Users,DC=IFTS,DC=local"
if required_group not in user_data.get('groups', []):
    logger.warning(f"Usuario {username} no pertenece al grupo requerido")
    return None
```

### Cambiar nivel de logging:

En `settings.py`, cambia el nivel de `INFO` a `DEBUG` para más detalles:

```python
'apps.juego.ldap_utils': {
    'handlers': ['console'],
    'level': 'DEBUG',  # <-- Cambiar aquí
},
```

## Troubleshooting

### Error: "No module named 'ldap3'"
```bash
pip install ldap3
```

### Error de conexión al servidor
- Verificar que el servidor AD esté accesible (ping)
- Verificar puerto 389 (LDAP) o 636 (LDAPS) esté abierto
- Verificar firewall

### Usuario no encontrado
- Verificar que `LDAP_AUTH_SEARCH_BASE` sea correcto
- Verificar que el usuario existe en AD
- Probar búsqueda manual con `test_ldap3_pure.py`

### Autenticación falla
- Verificar contraseña
- Verificar que la cuenta no esté bloqueada o deshabilitada
- Revisar logs en la consola (nivel INFO activado)

### Error de permisos
- Verificar que el usuario bind tenga permisos de lectura en AD
- Verificar DN del usuario bind

## Diferencias con django-python3-ldap

| Característica | django-python3-ldap | ldap3 puro (esta implementación) |
|----------------|---------------------|-----------------------------------|
| Dependencias | Muchas | Solo ldap3 |
| Control | Limitado | Total |
| Debugging | Difícil | Fácil (logs claros) |
| Configuración | Compleja | Simple |
| Mantenimiento | Dependes del paquete | Control total |
| Flexibilidad | Media | Alta |

## Próximos Pasos Sugeridos

1. Agregar cache para búsquedas de usuario frecuentes
2. Implementar sincronización periódica de grupos
3. Agregar soporte para múltiples dominios
4. Implementar cambio de contraseña desde Django
5. Agregar validación de políticas de contraseña de AD
