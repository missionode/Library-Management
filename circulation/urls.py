from django.urls import path
from . import views

urlpatterns = [
    path('issue/', views.IssueBookView.as_view(), name='issue_book'),
    path('return/', views.ReturnBookView.as_view(), name='return_book'),
    path('my-books/', views.MemberBorrowListView.as_view(), name='my_books'),
    path('renew/<int:pk>/', views.RenewBookView.as_view(), name='renew_book'),
    path('reserve/<int:pk>/', views.ReserveBookView.as_view(), name='reserve_book'),
    path('reservations/', views.ReservationListView.as_view(), name='reservation_list'),
]
