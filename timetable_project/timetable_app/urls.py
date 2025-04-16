from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CourseViewSet, TimeSlotViewSet, ConstraintViewSet, TimetableViewSet, TimetableEntryViewSet

router = DefaultRouter()
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'timeslots', TimeSlotViewSet, basename='timeslot')
router.register(r'constraints', ConstraintViewSet, basename='constraint')
router.register(r'timetables', TimetableViewSet, basename='timetable')
router.register(r'timetable-entries', TimetableEntryViewSet, basename='timetable-entry')

urlpatterns = [
    path('', include(router.urls)),
]