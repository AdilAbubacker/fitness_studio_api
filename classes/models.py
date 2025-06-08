from django.db import models
from django.db.models import Q


class ClassType(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Instructor(models.Model):
    name = models.CharField(max_length=100)
    class_type = models.ForeignKey(
        ClassType, 
        on_delete=models.CASCADE, 
        related_name='instructors'
        )

    def __str__(self):
        return f"{self.name} ({self.class_type.name})"


class ClassSession(models.Model):
    instructor = models.ForeignKey(
        Instructor, 
        on_delete=models.CASCADE, 
        related_name='sessions'
        )
    session_datetime = models.DateTimeField()
    total_slots = models.PositiveIntegerField()
    available_slots = models.PositiveIntegerField()


    class Meta:
        ordering = ['session_datetime']
        indexes = [
            # ensure a instructor doesn’t have multiple at same time
            models.Index(fields=["instructor", "session_datetime"]),
        ]
        constraints = [
            # Never allow available_slots to go negative
            models.CheckConstraint(
                check=Q(available_slots__gte=0),
                name="available_slots_non_negative"
            )
        ]

    def __str__(self):
        dt = self.session_datetime.strftime("%Y-%m-%d %H:%M")
        return f"{self.instructor.name} on {dt}"


    def save(self, *args, **kwargs):
        # On creation, if available_slots isn’t set, default it to total_slots
        if not self.pk and self.available_slots is None:
            self.available_slots = self.total_slots
        super().save(*args, **kwargs)
    

    @property
    def availability_status(self) -> str:
        if self.available_slots <= 0:
            return "sold_out"

        FAST_FILL_THRESHOLD_PERCENT = 20
        percent_left = (self.available_slots / self.total_slots) * 100

        if percent_left <= FAST_FILL_THRESHOLD_PERCENT:
            return "filling_fast"
        return "available"


