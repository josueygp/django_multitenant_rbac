from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from sandbox.models import Organization, Role, Member

class Command(BaseCommand):
    help = 'Injects test data to verify the Multi-tenant RBAC system'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('Starting data injection...'))

        # 1. Initial cleanup (Optional, prevents duplication if run multiple times)
        # Uncomment these lines if you want to wipe the DB before injecting
        # Member.objects.all().delete()
        # Role.objects.all().delete()
        # Organization.objects.all().delete()
        # User.objects.exclude(is_superuser=True).delete()

        # 2. Create Users
        # 'admin' usually exists (superuser), we create standard users here
        alice, _ = User.objects.get_or_create(username='alice', defaults={'email': 'alice@example.com'})
        alice.set_password('password123')
        alice.save()

        bob, _ = User.objects.get_or_create(username='bob', defaults={'email': 'bob@example.com'})
        bob.set_password('password123')
        bob.save()

        charlie, _ = User.objects.get_or_create(username='charlie', defaults={'email': 'charlie@example.com'})
        charlie.set_password('password123')
        charlie.save()

        self.stdout.write(self.style.SUCCESS(f'Users created: Alice, Bob, Charlie'))

        # 3. Create Tenants (Organizations)
        acme, _ = Organization.objects.get_or_create(name='Acme Corp')
        wayne, _ = Organization.objects.get_or_create(name='Wayne Enterprises')

        self.stdout.write(self.style.SUCCESS(f'Tenants created: {acme}, {wayne}'))

        # 4. Define Permissions (Using standard Django permissions)
        
        # A) User Permissions (from django.contrib.auth)
        content_type_user = ContentType.objects.get_for_model(User)
        perm_view_user = Permission.objects.get(content_type=content_type_user, codename='view_user')
        perm_add_user = Permission.objects.get(content_type=content_type_user, codename='add_user')

        # B) Role Permissions (from our sandbox app)
        # These are required so the Admin can access the Role Management views
        content_type_role = ContentType.objects.get_for_model(Role)
        perm_view_role = Permission.objects.get(content_type=content_type_role, codename='view_role')
        perm_add_role = Permission.objects.get(content_type=content_type_role, codename='add_role')
        perm_change_role = Permission.objects.get(content_type=content_type_role, codename='change_role')
        perm_delete_role = Permission.objects.get(content_type=content_type_role, codename='delete_role')

        # 5. Create Roles and Assign Permissions
        
        # --- Roles for ACME ---
        role_admin_acme, _ = Role.objects.get_or_create(
            name='Administrator', 
            organization=acme,
            defaults={'description': 'Full control in Acme'}
        )
        # The admin can view/create users AND view/create/edit/delete roles
        role_admin_acme.permissions.add(
            perm_view_user, perm_add_user,
            perm_view_role, perm_add_role,
            perm_change_role, perm_delete_role
        )

        role_employee_acme, _ = Role.objects.get_or_create(
            name='Employee', 
            organization=acme,
            defaults={'description': 'Limited access in Acme'}
        )
        # The employee can only view users (cannot manage roles)
        role_employee_acme.permissions.add(perm_view_user)


        # --- Roles for WAYNE (To test isolation) ---
        role_admin_wayne, _ = Role.objects.get_or_create(
            name='Director', # Different name to differentiate
            organization=wayne
        )
        # Director has full permissions in Wayne
        role_admin_wayne.permissions.add(perm_view_user, perm_add_user, perm_view_role, perm_add_role)

        self.stdout.write(self.style.SUCCESS('Roles created and permissions assigned'))

        # 6. Create Memberships (The final step that binds everything together)

        # Alice is Admin at Acme
        Member.objects.get_or_create(user=alice, organization=acme, defaults={'role': role_admin_acme})
        
        # Bob is Employee at Acme
        Member.objects.get_or_create(user=bob, organization=acme, defaults={'role': role_employee_acme})
        
        # Charlie is Director at Wayne (Has nothing to do with Acme)
        Member.objects.get_or_create(user=charlie, organization=wayne, defaults={'role': role_admin_wayne})

        # INTERESTING CASE: Alice is also a client/user at Wayne (Real Multitenancy)
        # But at Wayne she has no role (or we could assign a 'Guest' role)
        Member.objects.get_or_create(user=alice, organization=wayne, defaults={'role': None}) 

        self.stdout.write(self.style.SUCCESS('Memberships created successfully.'))
        self.stdout.write(self.style.SUCCESS('--- SETUP COMPLETED ---'))