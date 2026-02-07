from django.urls import reverse
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from tenant_rbac.mixins import TenantRBACMixin
from tenant_rbac.views import TenantListView, TenantCreateView, TenantDeleteView, TenantDetailView, TenantUpdateView
from .models import Role, Member
from .forms import RoleForm, MemberForm

class DashboardView(LoginRequiredMixin, TenantRBACMixin, TemplateView):
    template_name = "dashboard.html"
    # Required permission: view users (example)
    tenant_permission_required = 'auth.view_user'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Pass the tenant to the template (useful for displaying company name)
        context['tenant'] = self.request.tenant
        return context


class RoleDetailView(LoginRequiredMixin, TenantDetailView):
    model = Role
    template_name = "role_detail.html"
    context_object_name = "role"
    tenant_permission_required = 'sandbox.view_role'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add members of this role to context
        context['members'] = self.object.members.all()
        return context

class RoleDeleteView(TenantDeleteView):
    model = Role
    template_name = "role_confirm_delete.html" 
    tenant_permission_required = 'sandbox.delete_role'
    
    def get_success_url(self):
        return reverse('role_list', kwargs={'tenant_id': self.request.tenant.pk})

class RoleListView(LoginRequiredMixin, TenantListView):
    model = Role
    template_name = "role_list.html"
    context_object_name = "roles"
    tenant_permission_required = 'sandbox.view_role'

class RoleCreateView(LoginRequiredMixin, TenantCreateView):
    model = Role
    form_class = RoleForm
    template_name = "role_form.html"
    tenant_permission_required = 'sandbox.add_role'

    def get_success_url(self):
        return reverse('role_list', kwargs={'tenant_id': self.request.tenant.pk})

class MemberListView(LoginRequiredMixin, TenantListView):
    model = Member
    template_name = "member_list.html"
    context_object_name = "members"
    tenant_permission_required = 'auth.view_user' # Or a custom permission

class MemberUpdateView(LoginRequiredMixin, TenantUpdateView):
    model = Member
    form_class = MemberForm
    template_name = "member_form.html"
    tenant_permission_required = 'sandbox.change_role' # Using change_role as it affects role assignment

    def get_success_url(self):
        # Return to role detail if referred from there, or member list
        return reverse('member_list', kwargs={'tenant_id': self.request.tenant.pk})