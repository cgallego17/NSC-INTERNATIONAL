"""
URLs para gestión de archivos multimedia
"""
from django.urls import path

from . import views

app_name = 'media'

urlpatterns = [
    path('', views.MediaFileListView.as_view(), name='list'),
    path('create/', views.MediaFileCreateView.as_view(), name='create'),
    path('<int:pk>/', views.MediaFileDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.MediaFileUpdateView.as_view(), name='update'),
    path('<int:pk>/delete/', views.MediaFileDeleteView.as_view(), name='delete'),
    path('upload/', views.media_file_upload_ajax, name='upload_ajax'),
    path('bulk-delete/', views.media_file_bulk_delete, name='bulk_delete'),
    path('bulk-update/', views.media_file_bulk_update, name='bulk_update'),
    path('<int:pk>/update-ajax/', views.media_file_update_ajax, name='update_ajax'),
    path('list-ajax/', views.media_file_list_ajax, name='list_ajax'),
]

