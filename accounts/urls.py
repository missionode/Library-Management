from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    
    # Librarian Member Management
    path('members/', views.MemberManagementView.as_view(), name='member_list'),
    path('members/<int:pk>/', views.MemberDetailView.as_view(), name='member_detail'),
    path('members/<int:pk>/toggle/', views.ToggleMemberStatusView.as_view(), name='toggle_member_status'),
    path('members/<int:pk>/change-tier/', views.ChangeMembershipView.as_view(), name='change_membership'),
    path('members/<int:pk>/clear-fines/', views.ClearFinesView.as_view(), name='clear_fines'),
    path('members/create/', views.CreateMemberView.as_view(), name='create_member'),
    
    # Admin Librarian Management
    path('librarian/create/', views.CreateLibrarianView.as_view(), name='create_librarian'),
]
