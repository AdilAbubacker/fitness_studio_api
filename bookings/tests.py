# bookings/tests.py

from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
import pytz

from classes.management.commands.seed_data import Command as SeedCommand
from classes.models import ClassSession
from .models import Booking

class BookingViewTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # Seed the classes & sessions so we have something to book
        SeedCommand().handle()

    def setUp(self):
        # Common URL for both GET and POST
        self.url = reverse('bookings:booking')

    def test_create_and_list_booking(self):
        # 1) Pick a session with open slots
        session = ClassSession.objects.filter(available_slots__gt=0).first()
        self.assertIsNotNone(session, "No session available to book")

        # 2) Create a booking
        payload = {
            "session_id": session.id,
            "client_name": "Test User",
            "client_email": "test@example.com"
        }
        resp_post = self.client.post(self.url, payload, format='json')
        self.assertEqual(resp_post.status_code, status.HTTP_201_CREATED)
        booking_id = resp_post.json().get("booking_id")
        self.assertTrue(Booking.objects.filter(id=booking_id).exists())

        # 3) List bookings for that email
        resp_get = self.client.get(self.url + '?email=test@example.com',
                                   HTTP_X_TIMEZONE='Europe/London')
        self.assertEqual(resp_get.status_code, status.HTTP_200_OK)
        data = resp_get.json()
        # Expect exactly one booking returned
        self.assertEqual(len(data), 1)
        b = data[0]
        self.assertEqual(b['client_email'], 'test@example.com')
        # Check session_datetime was localized (contains + or - offset)
        self.assertRegex(b['session_datetime'], r'.*[+-]\d\d:\d\d$')

    def test_no_overbooking_race(self):
        # Create a session with exactly 1 slot
        base = ClassSession.objects.first()
        session = ClassSession.objects.create(
            instructor=base.instructor,
            session_datetime=timezone.now() + timezone.timedelta(days=1),
            total_slots=1,
            available_slots=1
        )

        payload = {
            "session_id": session.id,
            "client_name": "Racer",
            "client_email": "race@example.com"
        }

        # Fire two concurrent POSTs
        resp1 = self.client.post(self.url, payload, format='json')
        resp2 = self.client.post(self.url, payload, format='json')

        # One should succeed (201), the other fail (400)
        codes = sorted([resp1.status_code, resp2.status_code])
        self.assertEqual(codes, [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST])
