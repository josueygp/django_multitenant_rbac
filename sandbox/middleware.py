from django.shortcuts import get_object_or_404
from django_multitenant.utils import set_current_tenant
from .models import Organization

class SimpleTenantMiddleware:
    """
    Middleware SUPER SIMPLE para pruebas locales.
    Busca el tenant_id en la URL y activa el contexto.
    Ejemplo de URL: /<tenant_id>/dashboard/
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Lógica muy básica: si la URL empieza con un número, asumimos que es el ID del tenant
        path_parts = request.path.split('/')
        if len(path_parts) > 1 and path_parts[1].isdigit():
            tenant_id = path_parts[1]
            try:
                tenant = Organization.objects.get(pk=tenant_id)
                request.tenant = tenant
                set_current_tenant(tenant) # Esto configura django-multitenant internamente
            except Organization.DoesNotExist:
                pass # Si no existe, dejamos que la vista maneje el 404 si es necesario
        
        response = self.get_response(request)
        return response