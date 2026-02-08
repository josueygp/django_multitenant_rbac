# Django Multitenant RBAC Starter

Una arquitectura robusta para aplicaciones **SaaS B2B en Django**, diseñada para manejar múltiples inquilinos (tenants) con un sistema de Roles y Permisos (RBAC) totalmente aislado y seguro.

Este proyecto incluye una librería reutilizable (`tenant_rbac`) y un proyecto de demostración (`sandbox`).

## 🚀 Características Principales

*   **Multitenancy Nativo:** Basado en `django-multitenant` (CitusData) para un aislamiento eficiente a nivel de base de datos.
*   **RBAC Aislado:** Los roles y permisos son específicos por empresa. Un "Administrador" en la Empresa A no tiene acceso a la Empresa B.
*   **Vistas Genéricas Seguras:** `TenantCreateView`, `TenantListView`, etc., que inyectan y filtran el contexto del inquilino automáticamente.
*   **Prevención de Escalada de Privilegios:** Los administradores de un inquilino no pueden crear roles con más permisos de los que ellos mismos poseen.
*   **Integridad de Datos en Formularios:** Los formularios filtran automáticamente las claves foráneas (FK) para mostrar solo datos de la empresa actual.
*   **Gestión de Miembros:** Ver y asignar roles a usuarios dentro del inquilino eficientemente.
*   **Registros Protegidos:** Sistema `is_protected` para evitar la eliminación accidental o malintencionada de roles críticos (como el dueño o el admin principal).

---



## 📂 Estructura del Proyecto

```text
.
├── tenant_rbac/           # LIBRERÍA CORE (Reutilizable)
│   ├── mixins.py          # Mixins de seguridad para vistas
│   ├── models.py          # Modelos abstractos (Role, Member)
│   ├── forms.py           # Formularios con filtrado automático y anti-escalada
│   ├── views.py           # Vistas genéricas estrictas (ListView, CreateView...)
│   └── templatetags/      # Tags para controlar la UI según permisos
│
├── sandbox/               # PROYECTO DE IMPLEMENTACIÓN (Demo)
│   ├── models.py          # Modelos concretos (Organization, Role, Member)
│   ├── views.py           # Vistas de gestión de equipo (Roles y Miembros)
│   └── management/        # Comandos para datos de prueba
│
└── manage.py
```


## ⚡ Guía de Inicio Rápido

> [!WARNING]
> **Advertencia de Producción:**
> El proyecto usa `SimpleTenantMiddleware` en `sandbox/middleware.py`. Este middleware es **SOLO PARA PRUEBAS** (toma el ID de la URL).
> Para producción, debes implementar un middleware seguro que resuelva el tenant basado en subdominios (ej: `empresa.saas.com`) o tokens de sesión segura.

### 1. Instalación

```bash
# Clonar el repositorio
git clone <tu-repo>
cd django_multitenant_rbac

# Crear entorno virtual
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
# O si es manual: pip install django django-multitenant django-multitenant-rbac
```

### 2. Configuración de Base de Datos

```bash
# Migrar la base de datos
python manage.py makemigrations sandbox
python manage.py migrate
```

### 3. Inyección de Datos de Prueba

Hemos creado un comando personalizado que genera:

*   **Usuarios:** alice (Admin), bob (Empleado), charlie (Otra empresa).
*   **Empresas:** "Acme Corp" y "Wayne Enterprises".
*   **Roles:** Configurados con permisos reales.

```bash
python manage.py setup_test_data
```

### 4. Ejecutar Servidor

```bash
python manage.py runserver
```

*   **Login:** Ve a http://127.0.0.1:8000/login/
*   **Credenciales:** Usuario `alice`, Contraseña `password123`.
*   **Dashboard:** Serás redirigido automáticamente a tu empresa.

---

## 🛠️ Uso de la Librería `tenant_rbac`

Si deseas implementar esta lógica en tu propio proyecto, sigue estos patrones:

### INSTALACIÓN

```bash
pip install django-multitenant-rbac
```

### 1. Definición de Modelos (`models.py`)

Hereda de los modelos abstractos para ganar la funcionalidad automática.

```python
from django_multitenant.models import TenantModel
from tenant_rbac.models import AbstractTenantRole, AbstractTenantMember

class Role(AbstractTenantRole, TenantModel):
    # Campo estándar de seguridad
    is_protected = models.BooleanField(default=False)
    # ... configuración de FK a tu Tenant ...

class Member(AbstractTenantMember, TenantModel):
    # ... configuración de FK a tu Tenant ...
```

### 2. Vistas Seguras (`views.py`)

Usa las vistas de `tenant_rbac`. No uses las de Django directamente. Estas vistas garantizan que nadie vea ni cree datos fuera de su empresa.

```python
from tenant_rbac.views import TenantListView, TenantCreateView

class RoleListView(TenantListView):
    model = Role
    template_name = "role_list.html"
    tenant_permission_required = 'app.view_role'
    # ¡No hace falta get_queryset! El filtrado es automático.

class RoleCreateView(TenantCreateView):
    model = Role
    form_class = RoleForm
    template_name = "role_form.html"
    tenant_permission_required = 'app.add_role'
    # ¡No hace falta form_valid! La asignación de empresa es automática.
```

### 3. Formularios Blindados (`forms.py`)

Es obligatorio heredar de `TenantModelForm` o `RoleFormMixin`. Si no lo haces, la vista lanzará un error de seguridad (`ImproperlyConfigured`).

```python
from tenant_rbac.forms import RoleFormMixin, TenantModelForm

# Para gestión de Roles (Incluye Anti-Escalada)
class RoleForm(RoleFormMixin, forms.ModelForm):
    class Meta:
        model = Role
        fields = ['name', 'permissions', ...]

# Para otros modelos del tenant (ej. asignación de Miembros)
class MemberForm(TenantModelForm):
    class Meta:
        model = Member
        fields = ['role']
```

### 4. Template Tags (Uso en HTML)

Para controlar la visibilidad de elementos en tus plantillas según los permisos del tenant, usa el tag `has_tenant_perm`.

1. Carga los tags en tu template:

   ```html
   {% load rbac_tags %}
   ```

2. Verifica permisos:

   ```html
   {% has_tenant_perm 'app.crear_factura' as can_create_invoice %}

   {% if can_create_invoice %}
     <a href="{% url 'invoice_create' %}">Nueva Factura</a>
   {% endif %}
   ```

---

## 📖 Referencia de la API

| Componente | Tipo | Descripción |
| :--- | :--- | :--- |
| **`TenantRBACMixin`** | Mixin (View) | Verifica que el usuario tenga el permiso requerido (`tenant_permission_required`) dentro del tenant actual. |
| **`TenantGenericViewMixin`** | Mixin (View) | Sobrescribe `get_queryset` para filtrar automáticamente por el tenant actual. |
| **`TenantModelForm`** | Form | Filtra todos los campos `ForeignKey` del formulario para mostrar solo opciones que pertenecen al mismo tenant. |
| **`RoleFormMixin`** | Form Mixin | **Anti-Escalada:** Limita las opciones del campo `permissions` para que un usuario no pueda otorgar permisos que él mismo no tiene. |
| **`AbstractTenantRole`** | Model | Modelo base para Roles. Incluye nombre, descripción y relación M2M con `Permission`. |
| **`AbstractTenantMember`** | Model | Modelo base para Miembros. Vincula Usuario + Tenant (+ Rol en tu implementación concreta). |
| **`has_tenant_perm`** | Template Tag | Permite verificar permisos booleanos dentro de templates HTML. |

---

## ⚙️ Bajo el Capó: ¿Cómo funciona la seguridad?

Para generar confianza en la implementación, aquí explicamos los controles técnicos:

### 1. Inyección del Contexto (Middleware)
Todo comienza en el middleware. Antes de llegar a la vista, el sistema debe identificar al "Tenant Actual".
*   `request.tenant` se inyecta en cada petición.
*   `django_multitenant.utils.set_current_tenant(tenant)` se llama para activar el filtrado a nivel de base de datos (si usas Citus/Postgres schemas) o lógico.

### 2. Aislamiento en Vistas (`get_queryset`)
Nuestras vistas genéricas (`TenantListView`, etc.) sobrescriben `get_queryset`.
*   **Código:** `return qs.filter(tenant_id=request.tenant.id)`
*   **Efecto:** Incluso si un atacante cambia el ID en la URL (`/roles/999/`), la consulta SQL forzará el filtro `AND tenant_id = X`. Si el ID 999 no pertenece al tenant X, la base de datos devuelve vacío y Django lanza 404.

### 3. Formularios Blindados ("Anti-Leak")
Al crear o editar datos, el riesgo es ver información ajena en los "Select Box" (Claves Foráneas).
*   `TenantModelForm` itera sobre todos los campos del formulario.
*   Detecta si el modelo relacionado tiene `tenant_id`.
*   Aplica automáticamente un filtro al QuerySet del widget: `.filter(tenant_id=request.tenant.id)`.

### 4. Anti-Escalada de Privilegios
Evita que un administrador malintencionado o comprometido cree un "Super Usuario" oculto.
*   Al renderizar el formulario de Roles, `RoleFormMixin` intercepta el campo `permissions`.
*   Calcula la intersección entre "Todos los permisos disponibles" y "Los permisos que TIENE el usuario actual".
*   Solo muestra esa intersección. Nadie puede dar lo que no tiene.

---

## 🧪 Testing Manual

Para verificar la seguridad:

1.  Entra como **Alice** y ve a `/1/roles/`. Verás el rol "Administrador" con un candado (no borrable).
2.  Crea un rol "Becario". Verás que sí puedes borrarlo.
3.  Ve al **Dashboard** y haz clic en **"Ver Lista de Usuarios"**.
4.  Haz clic en **"Editar Rol"** para **Bob** y asígnale el rol "Administrador".
5.  Intenta entrar como **Charlie** (usuario de otra empresa) a `/1/roles/`. Recibirás un `403`.

---

## 📚 Referencias

- [django-multitenant](https://github.com/citusdata/django-multitenant)

---

## 📄 Licencia

Este proyecto es de código abierto bajo la licencia MIT.