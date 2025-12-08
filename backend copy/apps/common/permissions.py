"""
Custom permissions for the API
"""

from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """
    Permission to only allow owners of an object to view/edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Check if object has 'user' attribute
        if hasattr(obj, 'user'):
            return obj.user == request.user
        # Check if object has 'owner' attribute
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        # If object is the user themselves
        return obj == request.user


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Permission to allow read access to anyone, but write access only to owner.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner
        if hasattr(obj, 'user'):
            return obj.user == request.user
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        return obj == request.user


class IsCreatorOrAdmin(permissions.BasePermission):
    """
    Permission to allow creators and admins special access.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.role in ['creator', 'admin'] or request.user.is_staff
