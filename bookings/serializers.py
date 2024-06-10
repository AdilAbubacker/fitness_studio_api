from rest_framework import serializers
from .models import Booking
from rest_framework import serializers
from django.utils import timezone
from classes.models import ClassSession
from .models import Booking
from django.conf import settings
import pytz

class BookingCreateSerializer(serializers.Serializer):
    session_id = serializers.IntegerField()
    client_name = serializers.CharField()
    client_email = serializers.EmailField()  

class BookingListSerializer(serializers.ModelSerializer):
    session_datetime = serializers.SerializerMethodField()
    instructor = serializers.SerializerMethodField()
    class_type = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = [
            "id",
            "client_name",
            "client_email",
            "session_datetime",
            "instructor",
            "class_type",
        ]

    def get_session_datetime(self, obj):
        """
        Convert session_datetime (stored in UTC) to the user's timezone.
        We expect `user_tz` in the serializer context.
        """
        user_tz = self.context.get("user_tz")
        if not user_tz:
            user_tz = pytz.timezone(settings.TIME_ZONE)

        return timezone.localtime(obj.session.session_datetime, user_tz).isoformat()

    def get_instructor(self, obj):
        return obj.session.instructor.name

    def get_class_type(self, obj):
        return obj.session.instructor.class_type.name
