from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
import pytz

from .models import ClassType, Instructor, ClassSession
from classes.management.commands.seed_data import Command as SeedCommand


class ClassesAPITest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # Seed our data once for all tests in this class
        SeedCommand().handle()

    def test_list_class_types(self):
        url = reverse('classes:class-type-list')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        names = [c['name'] for c in resp.json()]
        self.assertIn('Yoga', names)
        self.assertIn('Zumba', names)
        self.assertIn('HIIT', names)

    def test_list_instructors(self):
        # pick Yoga ID dynamically
        yoga = ClassType.objects.get(name='Yoga')
        url = reverse('classes:instructor-list') + f'?class_type_id={yoga.id}'
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # each instructor record has a name and class_type
        for inst in resp.json():
            self.assertEqual(inst['class_type'], 'Yoga')

    def test_session_dates_filters_past(self):
        # Alice has one past + 3 future sessions from seed_data
        alice = Instructor.objects.get(name='Alice')
        url = reverse('classes:session-dates') + f'?instructor_id={alice.id}'
        # default TZ=Asia/Kolkata
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        dates = resp.json()
        # The oldest date returned should be today or after
        for d in dates:
            self.assertGreaterEqual(d, timezone.localdate().isoformat())

    def test_list_sessions_for_date(self):
        alice = Instructor.objects.get(name='Alice')
        dates = self.client.get(
            reverse('classes:session-dates') + f'?instructor_id={alice.id}'
        ).json()
        date = dates[0]
        url = reverse('classes:sessions-by-date') + f'?instructor_id={alice.id}&date={date}'
        resp = self.client.get(url, HTTP_X_TIMEZONE='America/New_York')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.json()
        for item in data:
            self.assertIn('session_time', item)
            self.assertIn('availability_status', item)
            self.assertIn(
                item['availability_status'],
                ['available', 'filling_fast', 'sold_out']
            )