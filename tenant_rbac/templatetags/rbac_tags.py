from django import template
from tenant_rbac.mixins import TenantRBACMixin

register = template.Library()

@register.simple_tag(takes_context=True)
def has_tenant_perm(context, permission_name):
    """
    Example: {% has_tenant_perm 'app.action' as can_edit %}
    {% if can_edit %} ... {% endif %}
    """
    request = context.get('request')
    if not request:
        return False


    mixin = TenantRBACMixin()
    mixin.tenant_permission_required = permission_name
    
    if not hasattr(request, 'tenant') and hasattr(context, 'tenant'):
        request.tenant = context['tenant']
        
    return mixin.has_tenant_permission(request)