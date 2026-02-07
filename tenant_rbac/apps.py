from django.apps import AppConfig

class TenantRbacConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tenant_rbac'
    verbose_name = "Tenant RBAC"