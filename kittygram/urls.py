from django.urls import path, include
from django.contrib import admin
from django.views.generic import RedirectView
from django.http import JsonResponse
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularJSONAPIView, SpectacularRedocView
from cats.api import AchievementViewSet, MyProfileView, TokenView
from showcase.views import CatViewSet, PublicCatViewSet, DailyTopViewSet, CatOfDayView, WeeklyTopView, MyVotesView

from cats.views import cat_list

router = DefaultRouter()
router.register('cats', CatViewSet, basename='cat')
router.register('achievements', AchievementViewSet, basename='achievement')
router.register('showcase/cats', PublicCatViewSet, basename='public-cat')
router.register('showcase/daily', DailyTopViewSet, basename='daily-top')

urlpatterns = [
   path('', RedirectView.as_view(url='/admin/', permanent=False)),
   path('health/', lambda request: JsonResponse({'status': 'ok'}), name='health'),
   path('cats/', cat_list),
   path('api/showcase/day/', CatOfDayView.as_view(), name='cat-of-day'),
   path('api/showcase/week/', WeeklyTopView.as_view(), name='weekly-top'),
   path('api/showcase/my-votes/', MyVotesView.as_view(), name='my-votes'),
   path('api/auth/token/', TokenView.as_view(), name='api-token'),
   path('api/users/me/', MyProfileView.as_view(), name='my-profile'),
   path('api/openapi.json', SpectacularJSONAPIView.as_view(authentication_classes=[], permission_classes=[]), name='openapi'),
   path('api/docs/', SpectacularRedocView.as_view(url_name='openapi', template_name='cats/docs.html', authentication_classes=[], permission_classes=[]), name='api-docs'),
   path('api/', include(router.urls)),
   path('api-auth/', include('rest_framework.urls')),
   path('admin/', admin.site.urls),
]


