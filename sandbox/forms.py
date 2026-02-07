from django import forms
from tenant_rbac.forms import RoleFormMixin
from .models import Role

class RoleForm(RoleFormMixin, forms.ModelForm): 
    permissions = forms.ModelMultipleChoiceField(
        queryset=None, 
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    class Meta:
        model = Role
        fields = ['name', 'description', 'permissions']

from tenant_rbac.forms import TenantModelForm
from .models import Member

class MemberForm(TenantModelForm):
    class Meta:
        model = Member
        fields = ['role']