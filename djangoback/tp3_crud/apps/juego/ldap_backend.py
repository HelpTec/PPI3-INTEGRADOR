"""
Backend de autenticación personalizado usando ldap3 puro
"""
import logging
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User
from .ldap_utils import LDAPConnection

logger = logging.getLogger(__name__)


class LDAP3Backend(BaseBackend):
    """
    Backend de autenticación personalizado que usa ldap3 puro
    para autenticar usuarios contra Active Directory
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Autentica un usuario contra Active Directory

        Args:
            request: HttpRequest object
            username: Nombre de usuario
            password: Contraseña

        Returns:
            User object si la autenticación es exitosa, None en caso contrario
        """
        if not username or not password:
            logger.warning("Intento de autenticación sin username o password")
            return None

        try:
            # Inicializar conexión LDAP
            ldap_conn = LDAPConnection()

            # Autenticar usuario contra AD
            user_data = ldap_conn.authenticate_user(username, password)

            if not user_data:
                logger.warning(f"Autenticación fallida para usuario: {username}")
                return None

            # Obtener o crear usuario de Django
            user, created = User.objects.get_or_create(
                username=username.lower(),
                defaults={
                    'first_name': user_data.get('first_name', ''),
                    'last_name': user_data.get('last_name', ''),
                    'email': user_data.get('email', ''),
                }
            )

            # Si el usuario ya existía, actualizar sus datos
            if not created:
                user.first_name = user_data.get('first_name', '')
                user.last_name = user_data.get('last_name', '')
                user.email = user_data.get('email', '')
                user.save()

            logger.info(f"Usuario autenticado exitosamente: {username} (created: {created})")
            return user

        except Exception as e:
            logger.error(f"Error en autenticación LDAP para {username}: {e}")
            return None

    def get_user(self, user_id):
        """
        Obtiene un usuario por su ID

        Args:
            user_id: ID del usuario

        Returns:
            User object o None si no existe
        """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
