from django.urls import path
from . import views

app_name = "classes"

urlpatterns = [
    path('class-types/', views.ClassTypeListView.as_view(), name='class-type-list'),
    path('instructors/', views.InstructorListByTypeView.as_view(), name='instructor-list'),
    path('session-dates/', views.SessionDatesByInstructorView.as_view(), name='session-dates'),
    path('sessions/', views.SessionListByInstructorDateView.as_view(), name="sessions-by-date"),
]
