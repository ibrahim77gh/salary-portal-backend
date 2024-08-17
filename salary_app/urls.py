from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ExcelUploadAPIView, EmployeeViewSet

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'employees', EmployeeViewSet)

urlpatterns = [
    path('upload-excel/', ExcelUploadAPIView.as_view(), name='upload-excel'),
    path('', include(router.urls)),
]
