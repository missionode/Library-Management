from django.urls import path
from . import views

urlpatterns = [
    path('notifications/', views.NotificationListView.as_view(), name='notifications'),
    path('notifications/<int:pk>/read/', views.MarkNotificationReadView.as_view(), name='mark_notification_read'),
    path('notifications/read-all/', views.MarkAllNotificationsReadView.as_view(), name='mark_all_notifications_read'),
    path('privacy/', views.PrivacyView.as_view(), name='privacy'),
    path('terms/', views.TermsView.as_view(), name='terms'),
    path('settings/', views.SettingsDashboardView.as_view(), name='settings_dashboard'),
    path('settings/config/', views.LibraryConfigurationUpdateView.as_view(), name='settings_config_edit'),
    path('settings/tiers/', views.MembershipTierListView.as_view(), name='settings_tier_list'),
    path('settings/tiers/add/', views.MembershipTierCreateView.as_view(), name='settings_tier_add'),
    path('settings/tiers/<int:pk>/edit/', views.MembershipTierUpdateView.as_view(), name='settings_tier_edit'),
]
