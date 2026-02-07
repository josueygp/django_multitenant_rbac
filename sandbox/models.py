from django.db import models
from django_multitenant.models import TenantModel
from tenant_rbac.models import AbstractTenantRole, AbstractTenantMember

from django.db.models.signals import post_save
from django.dispatch import receiver

class Organization(TenantModel):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    tenant_id = 'id'

    def __str__(self):
        return self.name

class Role(AbstractTenantRole, TenantModel):
    organization = models.ForeignKey(
        Organization, 
        on_delete=models.CASCADE, 
        related_name="roles"
    )
    is_protected = models.BooleanField(default=False)

    tenant_id = 'organization_id'

    class Meta(AbstractTenantRole.Meta):
        unique_together = ('organization', 'name') 

    def __str__(self):
        return f"{self.name} ({self.organization})"

class Member(AbstractTenantMember, TenantModel):

    organization = models.ForeignKey(
        Organization, 
        on_delete=models.CASCADE, 
        related_name="members"
    )
    role = models.ForeignKey(
        Role, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name="members"
    )
    is_protected = models.BooleanField(default=False)

    tenant_id = 'organization_id'

    class Meta:
        unique_together = ('organization', 'user')

    def __str__(self):
        return f"{self.user} in {self.organization}"

@receiver(post_save, sender=Organization)
def create_default_roles(sender, instance, created, **kwargs):
    if created:
        Role.objects.get_or_create(
            organization=instance, 
            name="Administrator",
            defaults={
                'description': 'Full access.',
                'is_protected': True
            }
        )
        Role.objects.get_or_create(
            organization=instance, 
            name="Member",
            defaults={'is_protected': False}
        )