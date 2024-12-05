# users/serializers.py
from rest_framework import serializers
from .models import CustomUser, UserFinancialProfile

class UserFinancialProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFinancialProfile
        fields = [
            'id', 
            'investment_experience', 
            'risk_tolerance', 
            'preferred_sectors', 
            'annual_income', 
            'net_worth'
        ]
        read_only_fields = ['id']
class UserSerializer(serializers.ModelSerializer):
    financial_profile = UserFinancialProfileSerializer(read_only=True)
    
    class Meta:
        model = CustomUser
        fields = [
            'id', 
            'email', 
            'username', 
            'full_name', 
            'account_type', 
            'date_joined', 
            'profile_photo',
            'financial_profile'
        ]
        read_only_fields = [ 'date_joined']

class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    confirm_password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    financial_profile = UserFinancialProfileSerializer(required=False)

    class Meta:
        model = CustomUser
        fields = [
             'id',
            'email', 
            'username', 
            'full_name', 
            'password', 
            'confirm_password', 
            'account_type',
            'profile_photo',
            'financial_profile'
        ]
        extra_kwargs = {
            'account_type': {'required': False},
            'id': {'required': True}  #
        }

    def validate(self, data):
        # Check password match
        if data['password'] != data.pop('confirm_password'):
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        
        return data

    def create(self, validated_data):
        # Extract financial profile data if provided
        financial_profile_data = validated_data.pop('financial_profile', None)
        
        # Create user
        password = validated_data.pop('password')
        user = CustomUser.objects.create_user(
            password=password,
            **validated_data
        )

        # Create financial profile if data is provided
        if financial_profile_data:
            financial_profile_data['id'] = user.id
            UserFinancialProfile.objects.create(
                user=user,
                **financial_profile_data
            )

        return user

class UserUpdateSerializer(serializers.ModelSerializer):
    financial_profile = UserFinancialProfileSerializer(required=False)

    class Meta:
        model = CustomUser
        fields = [
            'id',  
            'full_name', 
            'account_type',
            'profile_photo',
            'financial_profile'
        ]
        read_only_fields = ['id']  # Prevent ID modification
    def update(self, instance, validated_data):
        # Extract financial profile data if provided
        financial_profile_data = validated_data.pop('financial_profile', None)
        
        # Update user fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update or create financial profile
        if financial_profile_data:
            financial_profile, created = UserFinancialProfile.objects.get_or_create(
                user=instance,
                defaults={'id': instance.id}
            )
            for attr, value in financial_profile_data.items():
                setattr(financial_profile, attr, value)
            financial_profile.save()

        return instance

class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, style={'input_type': 'password'})
    new_password = serializers.CharField(required=True, style={'input_type': 'password'})
    confirm_new_password = serializers.CharField(required=True, style={'input_type': 'password'})

    def validate(self, data):
        # Check new passwords match
        if data['new_password'] != data['confirm_new_password']:
            raise serializers.ValidationError({"confirm_new_password": "New passwords do not match."})
        
        return data

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value

    def save(self):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user