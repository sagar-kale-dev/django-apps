from django.urls import path
from rest_framework_nested.routers import SimpleRouter, NestedSimpleRouter
from rest_framework_simplejwt.views import TokenRefreshView
from debug_toolbar.toolbar import debug_toolbar_urls
from . import views

router = SimpleRouter()
router.register(r'carts', views.CartViewSet)
router.register(r'orders', views.OrderViewSet, basename='orders')

carts_router = NestedSimpleRouter(router, r'carts', lookup='cart')
carts_router.register(r'items', views.CartItemViewSet,
                      basename='cart-items')

urlpatterns = [
    *router.urls,
    *debug_toolbar_urls(),
    *carts_router.urls,
    path('auth/login/', views.LoginView.as_view()),
    path('auth/token/refresh/', TokenRefreshView.as_view()),
    path('auth/profile/', views.ProfileView.as_view()),
    path('auth/register/', views.RegisterView.as_view()),
    path('auth/register/', views.RegisterView.as_view()),
]
