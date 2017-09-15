from django.contrib.auth.mixins import UserPassesTestMixin


class RegistrationPermissionMixin(UserPassesTestMixin):
    def test_func(self):
        if self.request.user.groups.filter(name='registration').exists():
            return True
        if self.request.user.groups.filter(name='db_admin').exists():
            return True
        if self.request.user.groups.filter(name='management').exists():
            return True
        if self.request.user.is_superuser:
            return True
        return False
