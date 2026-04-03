from decimal import Decimal, InvalidOperation
from datetime import datetime
from rest_framework import serializers
from .models import User, FinancialRecord


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "role", "is_active", "created_at"]
        read_only_fields = ["id", "created_at"]


class CreateUserSerializer(serializers.Serializer):
    username = serializers.CharField(min_length=3, max_length=80)
    email = serializers.EmailField()
    password = serializers.CharField(min_length=6, write_only=True)
    role = serializers.ChoiceField(choices=User.ROLE_CHOICES, default=User.VIEWER)

    def validate_username(self, value):
        qs = User.objects.filter(username=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Username already taken.")
        return value

    def validate_email(self, value):
        qs = User.objects.filter(email=value.lower())
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Email already registered.")
        return value.lower()

    def create(self, validated_data):
        user = User(
            username=validated_data["username"],
            email=validated_data["email"],
            role=validated_data.get("role", User.VIEWER),
        )
        user.set_password(validated_data["password"])
        user.save()
        return user


class UpdateUserSerializer(serializers.Serializer):
    username = serializers.CharField(min_length=3, max_length=80, required=False)
    email = serializers.EmailField(required=False)
    password = serializers.CharField(min_length=6, write_only=True, required=False)
    role = serializers.ChoiceField(choices=User.ROLE_CHOICES, required=False)

    def validate_username(self, value):
        if User.objects.filter(username=value).exclude(pk=self.instance.pk).exists():
            raise serializers.ValidationError("Username already taken.")
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value.lower()).exclude(pk=self.instance.pk).exists():
            raise serializers.ValidationError("Email already registered.")
        return value.lower()

    def update(self, instance, validated_data):
        for field in ["username", "email", "role"]:
            if field in validated_data:
                setattr(instance, field, validated_data[field])
        if "password" in validated_data:
            instance.set_password(validated_data["password"])
        instance.save()
        return instance


class FinancialRecordSerializer(serializers.ModelSerializer):
    created_by_username = serializers.SerializerMethodField()

    class Meta:
        model = FinancialRecord
        fields = [
            "id", "amount", "type", "category", "date",
            "notes", "created_by", "created_by_username",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_by", "created_at", "updated_at"]

    def get_created_by_username(self, obj):
        return obj.created_by.username if obj.created_by else None


class RecordWriteSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=Decimal("0.01"))
    type = serializers.ChoiceField(choices=FinancialRecord.TYPE_CHOICES)
    category = serializers.CharField(max_length=60)
    date = serializers.DateField()
    notes = serializers.CharField(allow_blank=True, allow_null=True, required=False)

    def create(self, validated_data):
        return FinancialRecord.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()
        return instance
