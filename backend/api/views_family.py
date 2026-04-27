import random
import string
from django.utils import timezone
from django.contrib.auth.models import User
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Family, FamilyMembership
from .permissions import IsAdminOfFamily, IsMemberOfFamily
from .serializers_family import (
    FamilySerializer,
    FamilyDetailSerializer,
    JoinFamilySerializer,
    CreateFamilySerializer,
    FamilyMembershipSerializer,
)


def generate_family_code():
    """Generate a 6-character uppercase alphanumeric code."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))


class FamilyViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def get_family_for_user(self, user):
        try:
            return user.membership.family
        except AttributeError:
            return None

    def get_membership_for_user(self, user):
        try:
            return user.membership
        except AttributeError:
            return None

    def list(self, request):
        """GET /api/family/ - Return current user's family details."""
        family = self.get_family_for_user(request.user)
        if not family:
            return Response(
                {"erro": "Você não está em nenhum grupo familiar."},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = FamilyDetailSerializer(family)
        return Response(serializer.data)

    def create(self, request):
        """POST /api/family/ - Create a new family group."""
        # Check if user already has a family
        if self.get_membership_for_user(request.user):
            return Response(
                {"erro": "Você já está em um grupo familiar. Saia antes de criar outro."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = CreateFamilySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"erro": "Dados inválidos", "detalhes": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        name = serializer.validated_data['name'].strip()
        if not name:
            return Response(
                {"erro": "O nome do grupo é obrigatório."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Generate unique code
        code = generate_family_code()
        while Family.objects.filter(code=code).exists():
            code = generate_family_code()

        family = Family.objects.create(
            name=name,
            code=code,
            code_expires_at=timezone.now() + timezone.timedelta(days=7),
            created_by=request.user
        )

        # Auto-create admin membership for creator
        FamilyMembership.objects.create(
            user=request.user,
            family=family,
            role='admin'
        )

        serializer = FamilyDetailSerializer(family)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request):
        """DELETE /api/family/ - Delete the family group (admin only)."""
        family = self.get_family_for_user(request.user)
        if not family:
            return Response(
                {"erro": "Você não está em nenhum grupo familiar."},
                status=status.HTTP_404_NOT_FOUND
            )

        membership = self.get_membership_for_user(request.user)
        if membership.role != 'admin':
            return Response(
                {"erro": "Apenas administradores podem excluir o grupo."},
                status=status.HTTP_403_FORBIDDEN
            )

        family.delete()
        return Response(
            {"mensagem": "Grupo excluído com sucesso."},
            status=status.HTTP_204_NO_CONTENT
        )

    @action(detail=False, methods=['post'], url_path='join')
    def join(self, request):
        """POST /api/family/join/ - Join a family via invite code."""
        # Check if user already has a family
        if self.get_membership_for_user(request.user):
            return Response(
                {"erro": "Você já está em um grupo familiar. Saia antes de entrar em outro."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = JoinFamilySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"erro": "Dados inválidos", "detalhes": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        code = serializer.validated_data['code']

        try:
            family = Family.objects.get(code=code)
        except Family.DoesNotExist:
            return Response(
                {"erro": "Código de convite inválido."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if timezone.now() > family.code_expires_at:
            return Response(
                {"erro": "Código de convite expirado. Peça ao administrador para gerar um novo."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create membership
        FamilyMembership.objects.create(
            user=request.user,
            family=family,
            role='member'
        )

        serializer = FamilyDetailSerializer(family)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], url_path='leave')
    def leave(self, request):
        """POST /api/family/leave/ - Leave the current family group."""
        membership = self.get_membership_for_user(request.user)
        if not membership:
            return Response(
                {"erro": "Você não está em nenhum grupo familiar."},
                status=status.HTTP_404_NOT_FOUND
            )

        family = membership.family

        # If admin and only member, delete family
        if membership.role == 'admin' and family.members.count() == 1:
            family.delete()
            return Response(
                {"mensagem": "Você saiu e o grupo foi excluído pois era o único membro."},
                status=status.HTTP_204_NO_CONTENT
            )

        # If admin and not only member, require transfer or reject
        if membership.role == 'admin' and family.members.count() > 1:
            # Find another member to transfer admin to
            new_admin = family.members.exclude(user=request.user).first()
            if new_admin:
                new_admin.role = 'admin'
                new_admin.save()

        membership.delete()
        return Response(
            {"mensagem": "Você saiu do grupo familiar."},
            status=status.HTTP_204_NO_CONTENT
        )

    @action(detail=False, methods=['post'], url_path='regenerate-code',
            permission_classes=[IsAuthenticated, IsAdminOfFamily])
    def regenerate_code(self, request):
        """POST /api/family/regenerate-code/ - Generate new invite code."""
        family = self.get_family_for_user(request.user)
        if not family:
            return Response(
                {"erro": "Você não está em nenhum grupo familiar."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Generate unique code
        code = generate_family_code()
        while Family.objects.filter(code=code).exists():
            code = generate_family_code()

        family.code = code
        family.code_expires_at = timezone.now() + timezone.timedelta(days=7)
        family.save(update_fields=['code', 'code_expires_at'])

        return Response({
            "code": family.code,
            "code_expires_at": family.code_expires_at.isoformat()
        })

    @action(detail=False, methods=['delete'], url_path=r'members/(?P<user_id>\d+)',
            permission_classes=[IsAuthenticated, IsAdminOfFamily])
    def remove_member(self, request, user_id=None):
        """DELETE /api/family/members/<user_id>/ - Remove a member (admin only)."""
        family = self.get_family_for_user(request.user)
        if not family:
            return Response(
                {"erro": "Você não está em nenhum grupo familiar."},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            target_user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response(
                {"erro": "Usuário não encontrado."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Cannot remove self
        if target_user == request.user:
            return Response(
                {"erro": "Você não pode se expulsar. Use 'Sair do Grupo' em vez disso."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            target_membership = FamilyMembership.objects.get(user=target_user, family=family)
        except FamilyMembership.DoesNotExist:
            return Response(
                {"erro": "Este usuário não é membro do seu grupo."},
                status=status.HTTP_404_NOT_FOUND
            )

        target_membership.delete()
        return Response(
            {"mensagem": "Membro removido com sucesso."},
            status=status.HTTP_204_NO_CONTENT
        )
