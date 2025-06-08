from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from datetime import timedelta

from classes.management.commands.seed_data import Command as SeedCommand
from classes.models import ClassSession
from bookings.models import Booking

class BookingViewTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        SeedCommand().handle()

    def setUp(self):
        self.url = reverse('bookings:booking')

    def test_create_and_list_booking(self):
        session = ClassSession.objects.filter(available_slots__gt=0).first()
        payload = {
            "session_id": session.id,
            "client_name": "Test User",
            "client_email": "test@example.com"
        }
        resp_post = self.client.post(self.url, payload, format='json')
        self.assertEqual(resp_post.status_code, status.HTTP_201_CREATED)
        booking_id = resp_post.json().get("booking_id")
        self.assertTrue(Booking.objects.filter(id=booking_id).exists())

        resp_get = self.client.get(self.url + "?email=test@example.com", HTTP_X_TIMEZONE="Asia/Kolkata")
        self.assertEqual(resp_get.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp_get.json()), 1)

    def test_no_overbooking_race(self):
        session = ClassSession.objects.create(
            instructor=ClassSession.objects.first().instructor,
            session_datetime=timezone.now() + timedelta(days=1),
            total_slots=1,
            available_slots=1
        )
        payload = {
            "session_id": session.id,
            "client_name": "Race User",
            "client_email": "race@example.com"
        }

        resp1 = self.client.post(self.url, payload, format='json')
        resp2 = self.client.post(self.url, payload, format='json')

        statuses = sorted([resp1.status_code, resp2.status_code])
        self.assertEqual(statuses, [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST])

    def test_prevent_duplicate_booking(self):
        session = ClassSession.objects.filter(available_slots__gt=0).first()
        email = "duplicate@example.com"

        payload = {
            "session_id": session.id,
            "client_name": "Dup User",
            "client_email": email
        }

        # First booking should succeed
        resp1 = self.client.post(self.url, payload, format='json')
        self.assertEqual(resp1.status_code, status.HTTP_201_CREATED)

        # Second booking for same session+email should fail
        resp2 = self.client.post(self.url, payload, format='json')
        self.assertEqual(resp2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("already booked", resp2.json().get("detail", "").lower())

    def test_prevent_past_booking(self):
        session = ClassSession.objects.filter(available_slots=0).first()  # The past one seeded with 0 slots
        payload = {
            "session_id": session.id,
            "client_name": "Past Guy",
            "client_email": "past@example.com"
        }

        resp = self.client.post(self.url, payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("past session", resp.json().get("detail", "").lower())

    def test_exact_slot_depletion(self):
        session = ClassSession.objects.create(
            instructor=ClassSession.objects.first().instructor,
            session_datetime=timezone.now() + timedelta(days=1),
            total_slots=2,
            available_slots=2
        )

        p1 = {"session_id": session.id, "client_name": "User1", "client_email": "u1@example.com"}
        p2 = {"session_id": session.id, "client_name": "User2", "client_email": "u2@example.com"}

        r1 = self.client.post(self.url, p1, format='json')
        r2 = self.client.post(self.url, p2, format='json')

        self.assertEqual(r1.status_code, 201)
        self.assertEqual(r2.status_code, 201)

        session.refresh_from_db()
        self.assertEqual(session.available_slots, 0)

    def test_get_booking_in_user_timezone(self):
        session = ClassSession.objects.filter(available_slots__gt=0).first()
        payload = {
            "session_id": session.id,
            "client_name": "Timezoner",
            "client_email": "tz@example.com"
        }
        self.client.post(self.url, payload, format='json')

        resp = self.client.get(self.url + "?email=tz@example.com", HTTP_X_TIMEZONE="America/New_York")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(len(data), 1)

        # session_datetime should end with a TZ offset like -04:00
        self.assertRegex(data[0]['session_datetime'], r".*[+-]\d{2}:\d{2}$")
