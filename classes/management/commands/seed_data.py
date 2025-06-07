# classes/management/commands/seed_data.py

from django.core.management.base import BaseCommand
from classes.models import ClassType, Instructor, ClassSession
from datetime import datetime, timedelta
import pytz

class Command(BaseCommand):
    help = "Seed sample class types, instructors, and sessions"

    def handle(self, *args, **kwargs):
        # Clear existing data
        ClassSession.objects.all().delete()
        Instructor.objects.all().delete()
        ClassType.objects.all().delete()

        print("Seeding data...")

        # 1. Create Class Types
        yoga = ClassType.objects.create(name="Yoga")
        zumba = ClassType.objects.create(name="Zumba")
        hiit = ClassType.objects.create(name="HIIT")

        # 2. Create Instructors
        alice = Instructor.objects.create(name="Alice", class_type=yoga)
        bob = Instructor.objects.create(name="Bob", class_type=zumba)
        charlie = Instructor.objects.create(name="Charlie", class_type=hiit)

        # 3. Create Sessions (some in the past, some in the future)
        ist = pytz.timezone("Asia/Kolkata")

        # -- Create 1 past session for Alice (yesterday at 08:00 IST) --
        aware_ist_now = datetime.now(ist)  # IST‐aware “now”
        aware_ist_yesterday = aware_ist_now - timedelta(days=1)
        naive_ist_yesterday = aware_ist_yesterday.replace(tzinfo=None)
        past_naive = naive_ist_yesterday.replace(hour=8, minute=0, second=0, microsecond=0)
        past_ist = ist.localize(past_naive)

        ClassSession.objects.create(
            instructor=alice,
            session_datetime=past_ist,
            total_slots=20,
            available_slots=0,  # Assume it was sold out
        )

        # -- Create 3 future days of sessions for each instructor --
        for i in range(3):
            # Future date in IST:
            future_ist_dt = (aware_ist_now + timedelta(days=i)).replace(
                hour=8, minute=0, second=0, microsecond=0, tzinfo=None
            )
            future_ist_dt = ist.localize(future_ist_dt)
            ClassSession.objects.create(
                instructor=alice,
                session_datetime=future_ist_dt,
                total_slots=20,
                available_slots=20,
            )

            future_ist_dt_bob = (aware_ist_now + timedelta(days=i)).replace(
                hour=10, minute=0, second=0, microsecond=0, tzinfo=None
            )
            future_ist_dt_bob = ist.localize(future_ist_dt_bob)
            ClassSession.objects.create(
                instructor=bob,
                session_datetime=future_ist_dt_bob,
                total_slots=15,
                available_slots=15,
            )

            future_ist_dt_charlie = (aware_ist_now + timedelta(days=i)).replace(
                hour=12, minute=0, second=0, microsecond=0, tzinfo=None
            )
            future_ist_dt_charlie = ist.localize(future_ist_dt_charlie)
            ClassSession.objects.create(
                instructor=charlie,
                session_datetime=future_ist_dt_charlie,
                total_slots=25,
                available_slots=25,
            )

        print("✅ Done seeding data.")
