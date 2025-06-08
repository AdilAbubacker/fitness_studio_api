# 🧘 Fitness Studio Booking API

A timezone-aware, concurrency-safe class booking system built with Django + Django REST Framework. Users can browse sessions (e.g. Yoga, Zumba), view instructors, and book available time slots without worrying about over-booking or timezone mismatches.

---

## ✅ Features

- 📚 **Class Types** — Yoga, Zumba, HIIT, etc.
- 👨‍🏫 **Instructors per Class Type**
- 📆 **Available Dates per Instructor** (excluding past dates)
- ⏰ **Sessions per Date** (with slot status: _Available_, _Filling Fast_, _Sold Out_)
- 📝 **Booking Endpoint** (handles concurrency + prevents overbooking)
- 📥 **My Bookings** — fetch bookings by user email

---

## ⚙️ Tech Stack

- **Backend**: Django 5.2, Django REST Framework
- **Database**: SQLite (for simplicity)
- **Timezone Handling**: Full support using `pytz` + `X-Timezone` header
- **Concurrency Safety**: PostgreSQL-style atomic slot decrement (`F()` + `CheckConstraint`)

---

## 🚀 Getting Started

```bash
git clone https://github.com/your-username/django-booking-api.git
cd django-booking-api

python -m venv .venv
source .venv/bin/activate      # On Windows: .venv\Scripts\activate

pip install -r requirements.txt

python manage.py migrate
python manage.py seed_data
python manage.py runserver
