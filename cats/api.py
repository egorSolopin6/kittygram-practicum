from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, serializers, viewsets
from rest_framework.authtoken.views import ObtainAuthToken
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiResponse
from .models import Achievement
from .serializers import AchievementSerializer


@extend_schema_view(list=extend_schema(summary='Справочник достижений'), retrieve=extend_schema(summary='Достижение по ID', responses={200: AchievementSerializer, 404: OpenApiResponse(description='Достижение не найдено.')}))
class AchievementViewSet(viewsets.ReadOnlyModelViewSet):
    """Публичный справочник достижений. Изменяется администратором в /admin/."""
    queryset = Achievement.objects.all()
    serializer_class = AchievementSerializer
    permission_classes = (permissions.AllowAny,)


class ProfileSerializer(serializers.ModelSerializer):
    groups = serializers.SlugRelatedField(many=True, read_only=True, slug_field='name')

    class Meta:
        model = get_user_model()
        fields = ('id', 'username', 'groups', 'is_staff', 'is_superuser')
        read_only_fields = fields


class MyProfileView(generics.RetrieveAPIView):
    """Собственный профиль и роли. Пароль и токен в ответ не включаются."""
    serializer_class = ProfileSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user


class TokenResponseSerializer(serializers.Serializer):
    token = serializers.CharField(read_only=True)


class TokenView(ObtainAuthToken):
    permission_classes = (permissions.AllowAny,)

    @extend_schema(summary='Вход и получение токена', auth=[], responses={200: TokenResponseSerializer, 400: OpenApiResponse(description='Неверные имя пользователя или пароль.')})
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
