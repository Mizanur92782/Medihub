from django.db import models
from django.conf import settings
from location.models import District, Division, Union, Upozila
from core.enum import GenderChoices, DayChoices


class Specialization(models.Model):
    name_eng = models.CharField(max_length=200, unique=True)
    name_bn = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name_eng


class SubSpecialization(models.Model):
    specialization = models.ForeignKey(Specialization, on_delete=models.CASCADE, related_name='sub_specializations')
    name_eng = models.CharField(max_length=200, unique=True)
    name_bn = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name_eng


class Qualification(models.Model):
    name_eng = models.CharField(max_length=200, unique=True)
    name_bn = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name_eng


class Hospital(models.Model):
    name_eng = models.CharField(max_length=200, unique=True)
    name_bn = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name_eng


class Doctor(models.Model):

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='doctor')
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=10, choices=GenderChoices.choices)
    profile_dp = models.ImageField(upload_to='doctor/dp/', blank=True, null=True)
    contact_number = models.CharField(max_length=15)

    division = models.ForeignKey(Division, on_delete=models.SET_NULL, null=True)
    district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True)
    upozila = models.ForeignKey(Upozila, on_delete=models.SET_NULL, null=True)
    union = models.ForeignKey(Union, on_delete=models.SET_NULL, null=True)
    
    specialization = models.ForeignKey(Specialization, on_delete=models.SET_NULL, null=True)
    sub_specialization = models.ForeignKey(SubSpecialization, on_delete=models.SET_NULL, null=True, blank=True)
    qualifications = models.ManyToManyField(Qualification, related_name='doctors', blank=True)
    hospital_affiliations = models.ManyToManyField(Hospital, related_name='doctors', blank=True)
    years_of_experience = models.PositiveIntegerField(default=0)
    license_number = models.CharField(max_length=100, unique=True)
    license_validity = models.DateField()
    
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Dr. {self.first_name} {self.last_name}'


class DoctorDetails(models.Model):
    doctor = models.OneToOneField(Doctor, on_delete=models.CASCADE, related_name='details')
    website = models.URLField(blank=True, null=True)
    social_link = models.URLField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    language = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return f'{self.doctor} - Details'


class DoctorEducation(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='educations')
    institution = models.CharField(max_length=200)
    degree = models.CharField(max_length=200)
    start_at = models.DateField()
    end_at = models.DateField(blank=True, null=True)

    def __str__(self):
        return f'{self.doctor} - {self.degree}'


class DoctorWorkingExperience(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='experiences')
    institution = models.CharField(max_length=200)
    position = models.CharField(max_length=200)
    starting_at = models.DateField()
    end_at = models.DateField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'{self.doctor} - {self.position}'


class DoctorScheduling(models.Model):

    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='schedules')
    day = models.CharField(max_length=10, choices=DayChoices.choices)
    start = models.TimeField()
    end = models.TimeField()

    def __str__(self):
        return f'{self.doctor} - {self.day}'


class DoctorRating(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='given_ratings')
    rating = models.PositiveSmallIntegerField(default=1)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('doctor', 'user')

    def __str__(self):
        return f'{self.doctor} - {self.rating}'
        