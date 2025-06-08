# bookings/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.db import transaction, IntegrityError
from django.db.models import F
from django.utils import timezone
from django.conf import settings

import pytz

from classes.models import ClassSession
from .models import Booking
from .serializers import BookingListSerializer


class BookingView(APIView):
    """
    GET  /api/bookings/?email=<client_email>
      → List all bookings for that email (times converted to user TZ)

    POST /api/bookings/
      Body: { session_id, client_name, client_email }
      → Atomically decrement slot + create booking
    """

    def get(self, request, *args, **kwargs):
        # 1. Require email query param
        raw_email = request.query_params.get("email", "")
        email = raw_email.strip() 

        if not email:
            return Response(
                {"detail": "email query parameter is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 2. Determine user TZ from header or default
        tz_header = request.headers.get("X-Timezone")
        try:
            user_tz = pytz.timezone(tz_header) if tz_header else pytz.timezone(settings.TIME_ZONE)
        except Exception:
            user_tz = pytz.timezone(settings.TIME_ZONE)

        # 3. Query the Booking model (case‐insensitive)
        bookings_qs = Booking.objects.filter(client_email__iexact=email).order_by("-booked_at")
        serializer = BookingListSerializer(bookings_qs, many=True, context={"user_tz": user_tz, 'm':email})
        return Response(serializer.data, status=status.HTTP_200_OK)


    def post(self, request, *args, **kwargs):
        data = request.data
        session_id     = data.get("session_id")
        client_name    = data.get("client_name")
        client_email   = data.get("client_email")

        # 1. input validation
        if not all([session_id, client_name, client_email]):
            return Response(
                {"detail": "session_id, client_name and client_email are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 2. Fast-fail checks
        try:
            session = ClassSession.objects.get(pk=session_id)
        except ClassSession.DoesNotExist:
            return Response({"detail": "Class session not found."}, status=status.HTTP_404_NOT_FOUND)

        if session.session_datetime < timezone.now():
            return Response({"detail": "Cannot book a past session."}, status=status.HTTP_400_BAD_REQUEST)

        if Booking.objects.filter(session=session, client_email=client_email).exists():
            return Response({"detail": "You have already booked this session."}, status=status.HTTP_400_BAD_REQUEST)

        if session.available_slots <= 0:
            return Response({"detail": "Session is fully booked."}, status=status.HTTP_400_BAD_REQUEST)
        
        # 3. decrement + insert in transaction
        try:
            with transaction.atomic():
                ClassSession.objects.filter(id=session_id).update(available_slots=F("available_slots") - 1)
                
                # create booking
                booking = Booking.objects.create(
                    session_id=session_id,
                    client_name=client_name,
                    client_email=client_email
                )

        except IntegrityError as e:
            msg = str(e).lower()
            if "available_slots_non_negative" in msg:
                return Response({"detail": "Session is fully booked."}, status=status.HTTP_400_BAD_REQUEST)
            
            return Response({"detail": "Booking failed: " + msg}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message": "Booking successful!", "booking_id": booking.id}, status=status.HTTP_201_CREATED)
