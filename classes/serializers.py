from rest_framework import serializers
from .models import ClassType, Instructor, ClassSession
from django.conf import settings
import pytz
from django.utils import timezone

class ClassTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassType
        fields = ["id", "name"]


class InstructorSerializer(serializers.ModelSerializer):
    class_type = serializers.CharField(source="class_type.name", read_only=True)

    class Meta:
        model = Instructor
        fields = ["id", "name", "class_type"]


class ClassSessionByDateSerializer(serializers.ModelSerializer):
    session_time = serializers.SerializerMethodField()
    availability_status = serializers.ReadOnlyField()

    class Meta:
        model = ClassSession
        fields = [
            "id",
            "session_time",
            "total_slots",
            "available_slots",
            "availability_status",
        ]

    # converting obj.session_datetime from UTC to the  user's timezone before returning.
    def get_session_time(self, obj):
        user_tz = self.context.get("user_tz")  
        if not user_tz:
            user_tz = pytz.timezone(settings.TIME_ZONE)

        # Convert UTC to user_tz
        local_dt = timezone.localtime(obj.session_datetime, user_tz)
        return local_dt.isoformat()
