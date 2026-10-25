from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.staff_login, name='staff_login'),
    path('logout/', views.staff_logout, name='staff_logout'),
    # ✅ The dashboard is now accessed at /developer/bugs/
    path('developer/bugs/', views.developer_dashboard, name='developer_dashboard'),
    path('developer/resolve/<int:bug_id>/', views.resolve_bug_remote, name='resolve_bug_remote'),
    path('api/receive-bug/', views.receive_bug_from_sims, name='receive_bug'),
]