from django.urls import path,include
from rest_framework.routers import DefaultRouter
from accounts import views

router = DefaultRouter()

router.register("user",views.CustomUserViewSet,basename="user")



urlpatterns = [
    path("",include(router.urls)),
    path("token",views.ObtainAuthToken.as_view())

]