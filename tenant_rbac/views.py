from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from .mixins import TenantRBACMixin
from .forms import TenantModelForm

class TenantGenericViewMixin:
    """
    Shared logic for field detection and filtering.
    """
    def get_tenant_field_name(self):
        if not self.model:
             if hasattr(self, 'get_queryset') and self.get_queryset() is not None:
                model = self.get_queryset().model
             else:
                raise ImproperlyConfigured(f"{self.__class__.__name__} must define 'model' or 'queryset'.")
        else:
            model = self.model
        return getattr(model, 'tenant_id', 'tenant_id')

    def get_queryset(self):
        qs = super().get_queryset()
        tenant = self.get_current_tenant(self.request)
        if not tenant: return qs.none()
        tenant_field = self.get_tenant_field_name()
        return qs.filter(**{tenant_field: tenant.pk})


class TenantListView(TenantRBACMixin, TenantGenericViewMixin, ListView):
    pass

class TenantDetailView(TenantRBACMixin, TenantGenericViewMixin, DetailView):
    pass

# --- STRICT SECURITY EDIT VIEWS ---

class TenantFormViewMixin(TenantGenericViewMixin):
    """
    Intermediate Mixin for Create/Update that forces the use of TenantModelForm
    and injects the request.
    """
    def get_form_class(self):
        form_class = super().get_form_class()
        # OPTION A (Strict): Yell if they don't use the secure form
        if not issubclass(form_class, TenantModelForm):
            raise ImproperlyConfigured(
                f"{self.__class__.__name__} uses {form_class.__name__}, which does NOT inherit from "
                f"tenant_rbac.forms.TenantModelForm. This is mandatory for security."
            )
        return form_class

    def get_form_kwargs(self):
        # Automatically inject request
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

class TenantCreateView(TenantRBACMixin, TenantFormViewMixin, CreateView):
    pass

class TenantUpdateView(TenantRBACMixin, TenantFormViewMixin, UpdateView):
    pass

# --- DELETE VIEW WITH FIELD PROTECTION ---

class TenantDeleteView(TenantRBACMixin, TenantGenericViewMixin, DeleteView):
    """
    Secure deletion. Checks 'is_protected' field.
    """
    def form_valid(self, form):
        # OPTION A: Standardization of the 'is_protected' field
        # If the object has is_protected=True, we forbid deletion.
        if getattr(self.object, 'is_protected', False):
            raise PermissionDenied("This record is protected and cannot be deleted.")
        
        return super().form_valid(form)
    
    # Support for GET requests (some implementations use GET to confirm)
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if getattr(self.object, 'is_protected', False):
             raise PermissionDenied("This record is protected and cannot be deleted.")
        return super().post(request, *args, **kwargs)