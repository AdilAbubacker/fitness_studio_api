# 🧘 Fitness Studio Booking API

A timezone-aware, concurrency-safe fitness class booking system built with Django + Django REST Framework. Users can browse sessions (e.g. Yoga, Zumba), view instructors, and book available time slots without worrying about over-booking or timezone mismatches.

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
- **Database**: SQLite3 
- **Timezone Handling**: `pytz` + `X-Timezone` header
- **Concurrency Safety**: DB constraints, transactions and atomic slot decrement (`F()` + `Updte`)

---

## 🧪 Postman Collection

Import this in Postman to test all endpoints:

👉 [`booking_api_postman_collection.json`](./postman/postman_collection.json)

---

## 🚀 Getting Started

```bash
git clone https://github.com/AdilAbubacker/fitness_studio_api.git
cd fitness_studio_api

python -m venv .venv
source .venv/bin/activate      # On Windows: .venv\Scripts\activate

pip install -r requirements.txt

python manage.py migrate
python manage.py seed_data
python manage.py runserver
