from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Family, FamilyMembership


class UserNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']


class FamilyMembershipSerializer(serializers.ModelSerializer):
    user = UserNestedSerializer(read_only=True)

    class Meta:
        model = FamilyMembership
        fields = ['id', 'user', 'role', 'joined_at']


class FamilySerializer(serializers.ModelSerializer):
    class Meta:
        model = Family
        fields = ['id', 'name', 'code', 'code_expires_at', 'created_by', 'created_at']
        read_only_fields = ['id', 'code', 'code_expires_at', 'created_by', 'created_at']


class FamilyDetailSerializer(serializers.ModelSerializer):
    members = FamilyMembershipSerializer(source='members.all', many=True, read_only=True)
    member_count = serializers.SerializerMethodField()

    class Meta:
        model = Family
        fields = ['id', 'name', 'code', 'code_expires_at', 'created_by', 'created_at', 'members', 'member_count']
        read_only_fields = ['id', 'code', 'code_expires_at', 'created_by', 'created_at', 'members', 'member_count']

    def get_member_count(self, obj):
        return obj.members.count()


class JoinFamilySerializer(serializers.Serializer):
    code = serializers.CharField(max_length=6, required=True)

    def validate_code(self, value):
        value = value.upper().strip()
        if len(value) != 6:
            raise serializers.ValidationError("O código deve ter 6 caracteres.")
        return value


class CreateFamilySerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100, required=True)
