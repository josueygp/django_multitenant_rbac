from django.core.exceptions import PermissionDenied, ImproperlyConfigured

class TenantRBACMixin:
    """
    Mixin to check permissions based on the current Tenant.
    """
    tenant_permission_required = None  # Example: 'sandbox.change_product'

    def get_current_tenant(self, request):
        """
        Attempts to retrieve the tenant from the request.
        Assumes you are using middleware that injects request.tenant
        or that you pass it manually.
        """
        if hasattr(request, 'tenant'):
            return request.tenant
        return None

    def has_tenant_permission(self, request):
        if not self.tenant_permission_required:
            return True 
        
        user = request.user
        if not user.is_authenticated:
            return False

        if user.is_superuser:
            return True

        tenant = self.get_current_tenant(request)
        if not tenant:
            return False

 
        membership_qs = user.tenant_memberships.all()
        member_model = membership_qs.model

        tenant_id_field = getattr(member_model, 'tenant_id', 'tenant_id')
        lookup = {tenant_id_field: tenant.pk}

        try:
            membership = membership_qs.filter(**lookup).select_related('role').first()
        except Exception:
            return False
        # -------------------------------

        if membership and membership.role:
            app_label, codename = self.tenant_permission_required.split('.')
            return membership.role.permissions.filter(
                content_type__app_label=app_label,
                codename=codename
            ).exists()
            
        return False

    def dispatch(self, request, *args, **kwargs):
        if not self.has_tenant_permission(request):
            raise PermissionDenied("You do not have sufficient permissions in this workspace.")
        return super().dispatch(request, *args, **kwargs)