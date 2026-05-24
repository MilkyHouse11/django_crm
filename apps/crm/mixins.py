from django.http import HttpResponseForbidden
    
class CheckPermissionsMixin:
    """
    A mixin that provides functionality for
    searching for user permissions by keyword
    """
    keyword = ""

    def dispatch(self, request, *args, **kwargs):
        required_permissions = [p for p in request.user.get_all_permissions() if self.keyword in p]

        if not required_permissions:
            print(f"USER PERMISSIONS: {required_permissions}")
            return HttpResponseForbidden()
    
        return super().dispatch(request, *args, **kwargs)
    