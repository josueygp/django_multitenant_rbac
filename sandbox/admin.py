from django.contrib import admin
from .models import Organization, Role, Member

class MemberInline(admin.TabularInline):
    model = Member
    extra = 1

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'tenant_id')
    inlines = [MemberInline]

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    # CAMBIO: Usamos 'organization' en lugar de 'tenant'
    list_display = ('name', 'organization') 
    list_filter = ('organization',)
    filter_horizontal = ('permissions',)

@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    # CAMBIO: Usamos 'organization' en lugar de 'tenant'
    list_display = ('user', 'role', 'organization')
    list_filter = ('organization', 'role')