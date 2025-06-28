
from rest_framework import permissions

class IsManager(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method not in permissions.SAFE_METHODS:
            if request.user.groups.filter(name='Manager').exists():
                return request.user.is_authenticated
            return False
        return True

class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user