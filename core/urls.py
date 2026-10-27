from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.staff_login, name='staff_login'),
    path('logout/', views.staff_logout, name='staff_logout'),
    path('developer/bugs/', views.developer_dashboard, name='developer_dashboard'),
    
    # Ticketing URLs
    path('bug/update/<int:bug_id>/', views.update_bug, name='update_bug'),
    path('bug/delete/<int:bug_id>/', views.delete_bug, name='delete_bug'),
    path('bug/notify/<int:bug_id>/', views.notify_user_resolved, name='notify_user_resolved'),
    
    # SIMS API Endpoint
    path('api/receive-bug/', views.receive_bug_from_sims, name='receive_bug'),
]