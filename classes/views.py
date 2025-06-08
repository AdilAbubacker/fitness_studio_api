from rest_framework import generics
from .models import ClassType, Instructor, ClassSession
from .serializers import ClassTypeSerializer, InstructorSerializer, ClassSessionByDateSerializer
from rest_framework.exceptions import ParseError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.conf import settings
import pytz
from datetime import datetime, time


class ClassTypeListView(generics.ListAPIView):
    queryset = ClassType.objects.all()
    serializer_class = ClassTypeSerializer


class InstructorListByTypeView(generics.ListAPIView):
    serializer_class = InstructorSerializer

    def get_queryset(self):
        """
        GET /api/classes/instructors/

        Return all instructors with query param: ?class_type_id=<int> class_type_id.
        """
        class_type_id = self.request.query_params.get("class_type_id")
        if not class_type_id:
            raise ParseError(detail="Missing required query param: class_type_id")

        try:
            class_type_id = int(class_type_id)
        except ValueError:
            raise ParseError(detail="class_type_id must be an integer")

        return Instructor.objects.filter(class_type_id=class_type_id).order_by("name")



class SessionDatesByInstructorView(APIView):
    """
    GET /api/classes/session-dates/?instructor_id=<int>
    
    Returns a JSON array of unique dates (YYYY-MM-DD) in the user's timezone 
    on which the given instructor has upcoming sessions. Header will include X-Timezone.
    """

    def get(self, request, *args, **kwargs):
        # 1. Require instructor_id as query param
        instructor_id = request.query_params.get("instructor_id")
        if not instructor_id:
            return Response(
                {"detail": "instructor_id query parameter is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 2. Fetch the instructor (404 if not found)
        try:
            instructor = Instructor.objects.get(pk=instructor_id)
        except Instructor.DoesNotExist:
            return Response(
                {"detail": f"Instructor with id={instructor_id} not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # 3. Determine user's timezone from header X-Timezone else settings.TIME_ZONE
        tz_header = request.headers.get("X-Timezone", None)
        if tz_header:
            try:
                user_tz = pytz.timezone(tz_header)
            except Exception:
                user_tz = pytz.timezone(settings.TIME_ZONE)
        else:
            user_tz = pytz.timezone(settings.TIME_ZONE)

        # 4. Filter ClassSession: only future sessions (session_datetime > now)
        now_utc = timezone.now()
        future_sessions = ClassSession.objects.filter(
            instructor=instructor,
            session_datetime__gt=now_utc,
        )

        # 5. Build a set of unique dates in user_tz
        unique_dates = set()
        for session in future_sessions:
            # Convert UTC‐stored datetime to user timezone
            local_dt = timezone.localtime(session.session_datetime, user_tz)
            unique_dates.add(local_dt.date())

        # 6. Sort and serialize dates as strings
        sorted_dates = sorted(unique_dates)
        date_list = [d.isoformat() for d in sorted_dates]

        return Response(date_list, status=status.HTTP_200_OK)



class SessionListByInstructorDateView(APIView):
    """
    GET /api/classes/sessions/?instructor_id=<int>&date=YYYY-MM-DD

    Returns all sessions (time slots) for the given instructor and date,
    converting times into the user's timezone. If a session_datetime (in UTC)
    falls within [start_of_day_in_UTC, end_of_day_in_UTC], we include it.
    
    """

    def get(self, request, *args, **kwargs):
        # 1. Validate query params
        instructor_id = request.query_params.get("instructor_id")
        date_str = request.query_params.get("date")  # "YYYY-MM-DD"

        if not instructor_id or not date_str:
            return Response(
                {"detail":"both instructor_id and date are required."},   
                status=status.HTTP_400_BAD_REQUEST,
                )

        # 2. Fetch the instructor (404 if not found)
        try:
            instructor = Instructor.objects.get(pk=instructor_id)
        except Instructor.DoesNotExist:
            return Response(
                {"detail": f"Instructor with id={instructor_id} not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # 3. Determine user's timezone from X-Timezone header (else default)
        tz_header = request.headers.get("X-Timezone", None)
        if tz_header:
            try:
                user_tz = pytz.timezone(tz_header)
            except Exception:
                user_tz = pytz.timezone(settings.TIME_ZONE)
        else:
            user_tz = pytz.timezone(settings.TIME_ZONE)

        # 4. Parse date_str to a Python date
        try:
            year, month, day = map(int, date_str.split("-"))
            user_date = datetime(year, month, day).date()
        except ValueError:
            return Response(
                {"detail": "date must be in YYYY-MM-DD format."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 5. Build the start/end of day in user_tz
        # make naive datetimes for midnight and next midnight
        naive_start = datetime.combine(user_date, time.min)  # 00:00:00
        naive_end = datetime.combine(user_date, time.max)    # 23:59:59.999999

        # localize them to user_tz
        localized_start = user_tz.localize(naive_start)
        localized_end = user_tz.localize(naive_end)

        # convert to UTC
        start_utc = localized_start.astimezone(pytz.UTC)
        end_utc = localized_end.astimezone(pytz.UTC)

        # 6. Query ClassSession with instructor AND session_datetime between start_utc and end_utc
        sessions_qs = ClassSession.objects.filter(
            instructor=instructor,
            session_datetime__gte=start_utc,
            session_datetime__lte=end_utc,
        ).order_by("session_datetime")


        # 7. Serialize, passing user_tz in context
        serializer = ClassSessionByDateSerializer(sessions_qs, many=True, context={"user_tz": user_tz})
        return Response(serializer.data, status=status.HTTP_200_OK)
