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

### 1. Installation

```bash
# Clone the repository
git clone <your-repo>
cd django_multitenant_rbac

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install django django-multitenant
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

---

## 🔒 Implemented Security Mechanisms

### 1. Privilege Escalation Prevention
A tenant administrator cannot grant permissions that they do not possess.

> **Example:** If Alice does not have the "Delete Invoices" permission, the role creation form will not show that option to assign it to another user.

### 2. Strict Isolation
All views inherit from `TenantGenericViewMixin`, which overrides `get_queryset`.

> **Result:** It is impossible to access an object `/roles/5/` if that role belongs to another company, even if you guess the ID.

### 3. Record Protection (`is_protected`)
The system respects the `is_protected` field in models.

*   **Usage:** The "Administrator" role is created with `is_protected=True`.
*   **Result:** If someone attempts to delete it via Web or API, they will receive a `403 Forbidden` error.

---

## 🧪 Manual Testing

To verify security:

1.  Log in as **Alice** and go to `/1/roles/`. You will see the "Administrator" role with a lock (not deletable).
2.  Create an "Intern" role. You will see that you can delete it.
3.  Go to **Dashboard** and click **"View User List"**.
4.  Click **"Edit Role"** for **Bob** and assign him the "Administrator" role.
5.  Try to log in as **Charlie** (user from another company) to `/1/roles/`. You will receive a `403`.

---

## 📄 License

This project is open source under the MIT license.
