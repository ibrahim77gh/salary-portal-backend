from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ExcelUploadAPIView, EmployeeViewSet, SalarySlipViewSet, NotificationViewSet, MarkNotificationsReadAPIView, UploadLogViewSet

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register('employee', EmployeeViewSet, basename='employees')
router.register('salary-slip', SalarySlipViewSet, basename='salary-slips')
router.register('notification', NotificationViewSet, basename='notifications')
router.register('upload-log', UploadLogViewSet, basename='upload-logs')

urlpatterns = [
    path('upload-excel/', ExcelUploadAPIView.as_view(), name='upload-excel'),
    path('notifications-read/', MarkNotificationsReadAPIView.as_view(), name='mark-notifications-read'),
    path('', include(router.urls)),
]
