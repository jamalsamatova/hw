from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers


User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(min_length=6, write_only=True)
    password_confirmation = serializers.CharField(min_length=6, write_only=True)
    first_name = serializers.CharField(max_length=50, write_only=True)
    last_name = serializers.CharField(max_length=100, write_only=True)


    class Meta:
        model = User
        fields = ('email', 'password', 'password_confirmation', 'first_name', 'last_name')

    def validate_email(self, email):
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError('User with given email already exists!')
        return email

    def validate(self, validated_data):
        password = validated_data.get('password')
        password_confirmation = validated_data.get('password_confirmation')
        if password_confirmation != password:
            raise serializers.ValidationError('Passwords do not match!')
        return validated_data

    def create(self, validated_data):
        email = validated_data.get('email')
        password = validated_data.get('password')
        first_name = validated_data.get('first_name')
        last_name = validated_data.get('last_name')
        user = User.objects.create_user(email, password, first_name, last_name)
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(style={'input_type': 'password'},
                                     trim_whitespace=False)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'),
                                username=email, password=password)
            if not user:
                msg = 'Unable to log in with provided credentials.'
                raise serializers.ValidationError(msg, code='authorization')

        else:
            msg = 'Must include username and password!'
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs