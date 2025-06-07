from django.urls import path
from . import views

urlpatterns = [
    path('class-types/', views.ClassTypeListView.as_view(), name='class-type-list'),
    path('instructors/', views.InstructorListByTypeView.as_view(), name='instructor-list'),
    path('sessions/dates/', views.SessionDatesByInstructorView.as_view(), name='session-dates'),
    path('sessions/', views.SessionListByInstructorDateView.as_view(), name='session-list'),
]
