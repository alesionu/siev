from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (
    ApiEstimateView,
    ApiSaveEstimationView,
    
    estimator_view,
    dashboard_view,
    estimation_detail_view,
    register_view,
    delete_estimation_view 
    
)

urlpatterns = [
    path('api/estimate/', ApiEstimateView.as_view(), name='api_estimate'),
    path('api/save-estimation/', ApiSaveEstimationView.as_view(), name='api_save_estimation'),

    path('', dashboard_view, name='dashboard'),
    
    path('estimate/', estimator_view, name='estimator'),
    
    path('estimation/<int:estimation_id>/', estimation_detail_view, name='estimation_detail'),
    
    path('login/', auth_views.LoginView.as_view(template_name='estimator/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', register_view, name='register'),
    
    path('delete/<int:estimation_id>/', delete_estimation_view, name='delete_estimation'),
]