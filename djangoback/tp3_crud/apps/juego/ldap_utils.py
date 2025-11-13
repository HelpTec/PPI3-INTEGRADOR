"""
Utilidades para trabajar con LDAP usando ldap3 puro
"""
import logging
from ldap3 import Server, Connection, ALL, SUBTREE
from django.conf import settings

logger = logging.getLogger(__name__)


class LDAPConnection:
    """
    Clase para manejar conexiones LDAP con Active Directory
    """

    def __init__(self):
        self.server_url = settings.LDAP_AUTH_URL
        self.bind_dn = settings.LDAP_AUTH_CONNECTION_USERNAME
        self.bind_password = settings.LDAP_AUTH_CONNECTION_PASSWORD
        self.search_base = settings.LDAP_AUTH_SEARCH_BASE
        self.use_tls = settings.LDAP_AUTH_USE_TLS

    def get_connection(self, user_dn=None, user_password=None):
        """
        Crea y retorna una conexión LDAP

        Args:
            user_dn: DN del usuario (opcional, usa bind_dn por defecto)
            user_password: Contraseña del usuario (opcional, usa bind_password por defecto)

        Returns:
            Connection object o None si falla
        """
        try:
            # Limpiar el URL
            server_host = self.server_url.replace('ldap://', '').replace('ldaps://', '')

            # Crear servidor
            server = Server(
                server_host,
                port=636 if self.use_tls else 389,
                use_ssl=self.use_tls,
                get_info=ALL
            )

            # Crear conexión
            conn = Connection(
                server,
                user=user_dn or self.bind_dn,
                password=user_password or self.bind_password,
                auto_bind=True,
                client_strategy='SYNC',
                receive_timeout=10
            )

            logger.info(f"Conexión LDAP exitosa para: {user_dn or self.bind_dn}")
            return conn

        except Exception as e:
            logger.error(f"Error conectando a LDAP: {e}")
            return None

    def search_user(self, username):
        """
        Busca un usuario en Active Directory por sAMAccountName

        Args:
            username: Nombre de usuario (sAMAccountName)

        Returns:
            dict con datos del usuario o None si no se encuentra
        """
        conn = self.get_connection()
        if not conn:
            return None

        try:
            search_filter = f"(sAMAccountName={username})"

            conn.search(
                search_base=self.search_base,
                search_filter=search_filter,
                search_scope=SUBTREE,
                attributes=[
                    'sAMAccountName',
                    'givenName',
                    'sn',
                    'mail',
                    'memberOf',
                    'distinguishedName'
                ]
            )

            if conn.entries:
                entry = conn.entries[0]
                user_data = {
                    'username': str(entry.sAMAccountName.value) if entry.sAMAccountName else username,
                    'first_name': str(entry.givenName.value) if entry.givenName else '',
                    'last_name': str(entry.sn.value) if entry.sn else '',
                    'email': str(entry.mail.value) if entry.mail else '',
                    'dn': str(entry.entry_dn),
                    'groups': [str(g) for g in entry.memberOf] if entry.memberOf else []
                }

                logger.info(f"Usuario encontrado: {username}")
                return user_data
            else:
                logger.warning(f"Usuario no encontrado: {username}")
                return None

        except Exception as e:
            logger.error(f"Error buscando usuario {username}: {e}")
            return None
        finally:
            conn.unbind()

    def authenticate_user(self, username, password):
        """
        Autentica un usuario contra Active Directory

        Args:
            username: Nombre de usuario (sAMAccountName)
            password: Contraseña del usuario

        Returns:
            dict con datos del usuario si la autenticación es exitosa, None en caso contrario
        """
        # Primero buscar el usuario para obtener su DN
        user_data = self.search_user(username)

        if not user_data:
            logger.warning(f"No se pudo encontrar el usuario: {username}")
            return None

        # Intentar autenticar con el DN del usuario
        try:
            server_host = self.server_url.replace('ldap://', '').replace('ldaps://', '')

            server = Server(
                server_host,
                port=636 if self.use_tls else 389,
                use_ssl=self.use_tls,
                get_info=ALL
            )

            # Intentar bind con las credenciales del usuario
            user_conn = Connection(
                server,
                user=user_data['dn'],
                password=password,
                auto_bind=True,
                client_strategy='SYNC',
                receive_timeout=10
            )

            # Si llegamos aquí, la autenticación fue exitosa
            user_conn.unbind()
            logger.info(f"Autenticación exitosa para: {username}")
            return user_data

        except Exception as e:
            logger.error(f"Error de autenticación para {username}: {e}")
            return None
