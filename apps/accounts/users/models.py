from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    email = models.EmailField(unique=True)
    username = None
    groups = None

    role = models.ForeignKey(
        'auth.group',
        verbose_name="role",
        blank=True,
        null=True,
        on_delete=models.DO_NOTHING,
        help_text=
            "The role this user belongs to. A user will get all permissions "
            "granted to his role.",
        related_name="users"
    )

    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email
    
    def get_group_permissions(self, obj=None):
        if not self.role:
            return set()
        
        permissions = set()
        for perm in self.role.permissions.all():
            permissions.add(f"{perm.content_type.app_label}.{perm.codename}")
        return permissions

    def get_all_permissions(self, obj=None):
        return self.get_group_permissions(obj)

    def has_perm(self, perm, obj=None):
        return perm in self.get_all_permissions()

    def has_module_perms(self, app_label):
        return any(
            perm.startswith(f'{app_label}.') 
            for perm in self.get_all_permissions()
        )

    @property
    def groups(self):
        from django.contrib.auth.models import Group
        if self.role:
            return Group.objects.filter(pk=self.role.pk)
        return Group.objects.none()