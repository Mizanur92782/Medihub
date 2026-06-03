from django.db import models

from authentication.models import User
from profiles.models.doctor_prof_mod import Doctor, Specialization


class UserDoctorInterest(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    specialization = models.ForeignKey(
        Specialization,
        on_delete=models.CASCADE
    )

    score = models.FloatField(default=0)

    updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "specialization")




class DoctorFeedImpression(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE
    )

    score = models.FloatField(default=0)

    shown_at = models.DateTimeField(auto_now_add=True)

    clicked = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=["user", "doctor"]),
        ]


class UserDoctorInteractionProfileShow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"User {self.user_id} clicked on Doctor {self.doctor_id} at {self.created_at}"
    


class UserDoctorInteractionFollwDoctor(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    follow = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"User {self.user_id} followed Doctor {self.doctor_id} at {self.created_at}"
    

class UserDoctorInteractionAskQuestion(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    question = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"User {self.user_id} asked a question to Doctor {self.doctor_id} at {self.created_at}"

class UserDoctorInteractionRateDoctor(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])  # Rating from 1
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"User {self.user_id} rated Doctor {self.doctor_id} with a rating of {self.rating} at {self.created_at}"

