from django.urls import path
from . import views

urlpatterns = [
    path('', views.BookListView.as_view(), name='book_list'),
    path('<int:pk>/', views.BookDetailView.as_view(), name='book_detail'),
    path('add/', views.BookCreateView.as_view(), name='book_add'),
    path('<int:pk>/edit/', views.BookUpdateView.as_view(), name='book_edit'),
    path('<int:pk>/delete/', views.BookDeleteView.as_view(), name='book_delete'),
    
    # Author & Category Management
    path('author/add/', views.AuthorCreateView.as_view(), name='author_add'),
    path('category/add/', views.CategoryCreateView.as_view(), name='category_add'),
]