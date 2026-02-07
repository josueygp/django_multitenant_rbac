from django import forms
from django.contrib.auth.models import Permission

class TenantModelForm(forms.ModelForm):
    """
    Mandatory base form for Create/Update Views in the library.
    Automatically filters ForeignKeys to show only data from the current tenant.
    """
    def __init__(self, *args, **kwargs):
        # Extract the request safely
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

        if not self.request:
            return

        tenant = getattr(self.request, 'tenant', None)
        
        if tenant:
            # 1. INTEGRITY: Filter all ForeignKeys to show only data from the tenant
            for field_name, field in self.fields.items():
                if isinstance(field, (forms.ModelChoiceField, forms.ModelMultipleChoiceField)):
                    # Security check in case the field has no queryset defined
                    if not hasattr(field, 'queryset') or field.queryset is None:
                        continue

                    model = field.queryset.model
                    # If the related model has tenant_id, we filter
                    if hasattr(model, 'tenant_id'):
                        tenant_field = getattr(model, 'tenant_id', 'tenant_id')
                        # Dynamic filter: organization_id=1
                        field.queryset = field.queryset.filter(**{tenant_field: tenant.pk})

    def save(self, commit=True):
        # Automatic assignment of the tenant on save (if it is creation)
        if self.request and not self.instance.pk:
            tenant = getattr(self.request, 'tenant', None)
            if tenant:
                tenant_field = getattr(self.instance, 'tenant_id', 'tenant_id')
                setattr(self.instance, tenant_field, tenant.pk)
        return super().save(commit)


class RoleFormMixin(TenantModelForm):
    """
    Security mixin to prevent Privilege Escalation.
    Usage: class RoleForm(RoleFormMixin, forms.ModelForm): ...
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # If the form has no 'permissions' field, we do nothing
        if not self.request or 'permissions' not in self.fields:
            return

        user = self.request.user
        
        # Global superuser sees everything
        if user.is_superuser:
            return

        # 2. ANTI-ESCALATION: Calculate allowed permissions
        allowed_permissions_qs = Permission.objects.none()
        
        tenant = getattr(self.request, 'tenant', None)
        if tenant:
            # Search for the current user's membership
            # Verify that the user has the 'tenant_memberships' relation
            if hasattr(user, 'tenant_memberships'):
                membership_model = user.tenant_memberships.model
                tenant_fk_name = getattr(membership_model, 'tenant_id', 'tenant_id')
                
                # Search for the membership in THIS tenant
                membership = user.tenant_memberships.filter(
                    **{tenant_fk_name: tenant.pk}
                ).select_related('role').first()

                if membership and membership.role:
                    # The user can ONLY see/assign permissions that THEY HAVE
                    allowed_permissions_qs = membership.role.permissions.all()

        # Intercept the QuerySet of the permissions field
        self.fields['permissions'].queryset = allowed_permissions_qs