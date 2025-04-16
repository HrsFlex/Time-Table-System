from django.db import models
from django.contrib.auth.models import User

class Course(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='courses')
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20)
    instructor = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    color = models.CharField(max_length=20, default="#3498db")  # Default blue color
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.code}: {self.name}"

class TimeSlot(models.Model):
    DAY_CHOICES = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]
    
    SLOT_TYPES = [
        ('lecture', 'Lecture'),
        ('lab', 'Laboratory'),
        ('tutorial', 'Tutorial'),
        ('other', 'Other')
    ]
    
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='time_slots')
    day_of_week = models.IntegerField(choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    location = models.CharField(max_length=100, blank=True, null=True)
    slot_type = models.CharField(max_length=20, choices=SLOT_TYPES, default='lecture')
    
    def __str__(self):
        return f"{self.course.code} - {self.get_day_of_week_display()} {self.start_time}-{self.end_time}"

class Constraint(models.Model):
    CONSTRAINT_TYPES = [
        ('preferred', 'Preferred Time'),
        ('avoid', 'Avoid Time'),
        ('required', 'Required Free Time'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='constraints')
    constraint_type = models.CharField(max_length=20, choices=CONSTRAINT_TYPES)
    day_of_week = models.IntegerField(choices=TimeSlot.DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    
    def __str__(self):
        return f"{self.get_constraint_type_display()} - {self.get_day_of_week_display()} {self.start_time}-{self.end_time}"

class Timetable(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='timetables')
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.user.username}"

class TimetableEntry(models.Model):
    timetable = models.ForeignKey(Timetable, on_delete=models.CASCADE, related_name='entries')
    timeslot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ('timetable', 'timeslot')
    
    def __str__(self):
        return f"{self.timetable.name} - {self.timeslot}"