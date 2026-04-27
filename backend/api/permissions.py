from rest_framework import permissions
from django.utils import timezone


class IsAdminOfFamily(permissions.BasePermission):
    """Permission that checks if the user is an admin of their family."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        try:
            return request.user.membership.role == 'admin'
        except AttributeError:
            return False


class IsMemberOfFamily(permissions.BasePermission):
    """Permission that checks if the user belongs to a family."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        try:
            return hasattr(request.user, 'membership')
        except AttributeError:
            return False


class GastoPermission(permissions.BasePermission):
    """
    Permission for Gasto objects:
    - Creator can always read/write their own gastos
    - Admin of the same family can edit/delete gastos created AFTER
      the member joined the family
    - Members can only read gastos of the same family
    """

    def has_object_permission(self, request, view, obj):
        user = request.user
        # Creator always has full access
        if obj.user == user:
            return True

        # Check if user is admin of the same family as the gasto
        try:
            user_membership = user.membership
        except AttributeError:
            return False

        if not obj.family:
            return False

        if user_membership.family != obj.family:
            return False

        if user_membership.role != 'admin':
            return False

        # Admin can only edit/delete gastos created after member joined
        # For safe access, check if any membership exists where joined_at <= gasto.criado_em
        from .models import FamilyMembership
        member = FamilyMembership.objects.filter(
            family=obj.family,
            user=obj.user,
            joined_at__lte=obj.criado_em
        ).first()

        return member is not None
