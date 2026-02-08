# Django Multitenant RBAC Starter

A robust architecture for **B2B SaaS applications in Django**, designed to handle multiple tenants with a fully isolated and secure Role-Based Access Control (RBAC) system.

This project includes a reusable library (`tenant_rbac`) and a demo project (`sandbox`).

## 🚀 Key Features

*   **Native Multitenancy:** Based on `django-multitenant` (CitusData) for efficient database-level isolation.
*   **Isolated RBAC:** Roles and permissions are company-specific. An "Administrator" in Company A has no access to Company B.
*   **Secure Generic Views:** `TenantCreateView`, `TenantListView`, etc., which automatically inject and filter the tenant context.
*   **Privilege Escalation Prevention:** Tenant administrators cannot create roles with more permissions than they possess themselves.
*   **Data Integrity in Forms:** Forms automatically filter Foreign Keys (FK) to show only data from the current company.
*   **Member Management:** View and assign roles to users within the tenant efficiently.
*   **Protected Records:** `is_protected` system to prevent accidental or malicious deletion of critical roles (like the owner or main admin).

---

## 📂 Project Structure

```text
.
├── tenant_rbac/           # CORE LIBRARY (Reusable)
│   ├── mixins.py          # Security mixins for views
│   ├── models.py          # Abstract models (Role, Member)
│   ├── forms.py           # Forms with automatic filtering and anti-escalation
│   ├── views.py           # Strict generic views (ListView, CreateView...)
│   └── templatetags/      # Tags to control UI based on permissions
│
├── sandbox/               # IMPLEMENTATION PROJECT (Demo)
│   ├── models.py          # Concrete models (Organization, Role, Member)
│   ├── views.py           # Team management views (Roles & Members)
│   └── management/        # Commands for test data
│
└── manage.py
```

## ⚡ Quick Start Guide

> [!WARNING]
> **Production Warning:**
> The project uses `SimpleTenantMiddleware` in `sandbox/middleware.py`. This middleware is **FOR TESTING ONLY** (it takes the ID from the URL).
> For production, you must implement a secure middleware that resolves the tenant based on subdomains (e.g., `company.saas.com`) or secure session tokens.

### 1. Installation

```bash
# Clone the repository
git clone <your-repo>
cd django_multitenant_rbac

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
# Or manually: pip install django django-multitenant django-multitenant-rbac
```

### 2. Database Configuration

```bash
# Migrate the database
python manage.py makemigrations sandbox
python manage.py migrate
```

### 3. Test Data Injection

We have created a custom command that generates:

*   **Users:** alice (Admin), bob (Employee), charlie (Another company).
*   **Companies:** "Acme Corp" and "Wayne Enterprises".
*   **Roles:** Configured with real permissions.

```bash
python manage.py setup_test_data
```

### 4. Run Server

```bash
python manage.py runserver
```

*   **Login:** Go to http://127.0.0.1:8000/login/
*   **Credentials:** User `alice`, Password `password123`.
*   **Dashboard:** You will be automatically redirected to your company.

---

## 🛠️ Using the `tenant_rbac` Library

If you wish to implement this logic in your own project, follow these patterns:

### INSTALLATION

```bash
pip install django-multitenant-rbac
```

### 1. Model Definition (`models.py`)

Inherit from the abstract models to gain automatic functionality.

```python
from django_multitenant.models import TenantModel
from tenant_rbac.models import AbstractTenantRole, AbstractTenantMember

class Role(AbstractTenantRole, TenantModel):
    # Standard security field
    is_protected = models.BooleanField(default=False)
    # ... FK configuration to your Tenant ...

class Member(AbstractTenantMember, TenantModel):
    # ... FK configuration to your Tenant ...
```

### 2. Secure Views (`views.py`)

Use the `tenant_rbac` views. Do not use Django's directly. These views ensure that no one sees or creates data outside their company.

```python
from tenant_rbac.views import TenantListView, TenantCreateView

class RoleListView(TenantListView):
    model = Role
    template_name = "role_list.html"
    tenant_permission_required = 'app.view_role'
    # No need for get_queryset! Filtering is automatic.

class RoleCreateView(TenantCreateView):
    model = Role
    form_class = RoleForm
    template_name = "role_form.html"
    tenant_permission_required = 'app.add_role'
    # No need for form_valid! Company assignment is automatic.
```

### 3. Armored Forms (`forms.py`)

It is mandatory to inherit from `TenantModelForm` or `RoleFormMixin`. If you don't, the view will raise a security error (`ImproperlyConfigured`).

```python
from tenant_rbac.forms import RoleFormMixin, TenantModelForm

# For Role management (Includes Anti-Escalation)
class RoleForm(RoleFormMixin, forms.ModelForm):
    class Meta:
        model = Role
        fields = ['name', 'permissions', ...]

# For other tenant models (e.g. Member assignment)
class MemberForm(TenantModelForm):
    class Meta:
        model = Member
        fields = ['role']
```

### 4. Template Tags (HTML Usage)

To control the visibility of elements in your templates based on tenant permissions, use the `has_tenant_perm` tag.

1. Load the tags in your template:

   ```html
   {% load rbac_tags %}
   ```

2. Check permissions:

   ```html
   {% has_tenant_perm 'app.create_invoice' as can_create_invoice %}

   {% if can_create_invoice %}
     <a href="{% url 'invoice_create' %}">New Invoice</a>
   {% endif %}
   ```

---

## 📖 API Reference

| Component | Type | Description |
| :--- | :--- | :--- |
| **`TenantRBACMixin`** | Mixin (View) | Verifies that the user has the required permission (`tenant_permission_required`) within the current tenant. |
| **`TenantGenericViewMixin`** | Mixin (View) | Overrides `get_queryset` to automatically filter by the current tenant. |
| **`TenantModelForm`** | Form | Filters all `ForeignKey` fields in the form to show only options belonging to the same tenant. |
| **`RoleFormMixin`** | Form Mixin | **Anti-Escalation:** Limits the options of the `permissions` field so that a user cannot grant permissions they do not have themselves. |
| **`AbstractTenantRole`** | Model | Base model for Roles. Includes name, description, and M2M relationship with `Permission`. |
| **`AbstractTenantMember`** | Model | Base model for Members. Links User + Tenant (+ Role in your concrete implementation). |
| **`has_tenant_perm`** | Template Tag | Allows verifying boolean permissions within HTML templates. |

---

## ⚙️ Under the Hood: How Security Works

To build trust in the implementation, here we explain the technical controls:

### 1. Context Injection (Middleware)
Everything starts in the middleware. Before reaching the view, the system must identify the "Current Tenant".
*   `request.tenant` is injected into every request.
*   `django_multitenant.utils.set_current_tenant(tenant)` is called to activate database-level filtering (if using Citus/Postgres schemas) or logical filtering.

### 2. View Isolation (`get_queryset`)
Our generic views (`TenantListView`, etc.) override `get_queryset`.
*   **Code:** `return qs.filter(tenant_id=request.tenant.id)`
*   **Effect:** Even if an attacker changes the ID in the URL (`/roles/999/`), the SQL query will force the filter `AND tenant_id = X`. If ID 999 does not belong to tenant X, the database returns empty and Django raises a 404.

### 3. Armored Forms ("Anti-Leak")
When creating or editing data, the risk is seeing foreign data in "Select Boxes" (Foreign Keys).
*   `TenantModelForm` iterates over all fields in the form.
*   Detects if the related model has `tenant_id`.
*   Automatically applies a filter to the widget's QuerySet: `.filter(tenant_id=request.tenant.id)`.

### 4. Privilege Escalation Prevention
Prevents a malicious or compromised administrator from creating a hidden "Super User".
*   When rendering the Role form, `RoleFormMixin` intercepts the `permissions` field.
*   Calculates the intersection between "All available permissions" and "Permissions the current user HAS".
*   Only displays that intersection. No one can give what they do not have.

---

## 🧪 Manual Testing

To verify security:

1.  Log in as **Alice** and go to `/1/roles/`. You will see the "Administrator" role with a lock (not deletable).
2.  Create an "Intern" role. You will see that you can delete it.
3.  Go to **Dashboard** and click **"View User List"**.
4.  Click **"Edit Role"** for **Bob** and assign him the "Administrator" role.
5.  Try to log in as **Charlie** (user from another company) to `/1/roles/`. You will receive a `403`.

---

## 📚 References

- [django-multitenant](https://github.com/citusdata/django-multitenant)

---

## 📄 License

This project is open source under the MIT license.