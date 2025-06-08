# classes/management/commands/seed_data.py

from django.core.management.base import BaseCommand
from classes.models import ClassType, Instructor, ClassSession
from datetime import timedelta
from django.utils import timezone
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

        # 3. Create Sessions (some past, some future) in IST
        ist = pytz.timezone("Asia/Kolkata")
        now_ist = timezone.localtime(timezone.now(), ist)

        # -- 1 Past session for Alice (yesterday at 08:00 IST)
        past_ist = (now_ist - timedelta(days=1)).replace(hour=8, minute=0, second=0, microsecond=0)
        ClassSession.objects.create(
            instructor=alice,
            session_datetime=past_ist,
            total_slots=20,
            available_slots=0,
        )

        # -- Future sessions for next 3 days --
        for i in range(1, 4):
            day_ist = now_ist + timedelta(days=i)

            alice_dt = day_ist.replace(hour=8, minute=0, second=0, microsecond=0)
            bob_dt = day_ist.replace(hour=10, minute=0, second=0, microsecond=0)
            charlie_dt = day_ist.replace(hour=12, minute=0, second=0, microsecond=0)

            ClassSession.objects.create(
                instructor=alice,
                session_datetime=alice_dt,
                total_slots=20,
                available_slots=20,
            )
            ClassSession.objects.create(
                instructor=bob,
                session_datetime=bob_dt,
                total_slots=15,
                available_slots=15,
            )
            ClassSession.objects.create(
                instructor=charlie,
                session_datetime=charlie_dt,
                total_slots=25,
                available_slots=25,
            )

        print("✅ Done seeding data.")
