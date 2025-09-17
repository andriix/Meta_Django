from django.ulrs import path
from . import views

urlpatterns = [
    path('books/', views.books)
]