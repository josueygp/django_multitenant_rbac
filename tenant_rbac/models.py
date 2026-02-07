from django.db import models
from django.conf import settings
from django.contrib.auth.models import Permission
from django.utils.translation import gettext_lazy as _

class AbstractTenantRole(models.Model):
    """
    Abstract model to define roles within a tenant.
    
    Usage:
        You must inherit from this class and your Tenant base class (e.g. TenantModel)
        and add the ForeignKey field to your Tenant model.
    """
    name = models.CharField(
        _("Role Name"), 
        max_length=100,
        help_text=_("Example: Administrator, Salesperson, Editor")
    )
    description = models.TextField(
        _("Description"), 
        blank=True,
        help_text=_("Brief description of the responsibilities of this role.")
    )
    
    # Relationship with Django's native permission system.
    # No need to reinvent the wheel; we use Django's ContentTypes and Permissions.
    permissions = models.ManyToManyField(
        Permission,
        verbose_name=_("Permissions"),
        blank=True,
        help_text=_("Select specific permissions that this role will have within the tenant.")
    )

    class Meta:
        abstract = True
        verbose_name = _("Business Role")
        verbose_name_plural = _("Business Roles")
        ordering = ['name']

    def __str__(self):
        return self.name


class AbstractTenantMember(models.Model):
    """
    Abstract model to link a user to a tenant with a specific role.
    
    Usage:
        Inherit from this class and add:
        1. The 'tenant' field (ForeignKey).
        2. The 'role' field (ForeignKey to your concrete Role model).
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tenant_memberships",
        verbose_name=_("User"),
        help_text=_("The user belonging to this workspace.")
    )
    
    # Note: We do not define 'role' or 'tenant' here to avoid circular dependencies
    # and allow the developer to choose their field names and relationship types
    # (for example, if using UUIDs or Integers).

    class Meta:
        abstract = True
        verbose_name = _("Team Member")
        verbose_name_plural = _("Team Members")

    def __str__(self):
        return f"Membership: {self.user}"