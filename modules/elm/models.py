from django.contrib.auth.models import User
from django.db import models


class LeaveType(models.Model):
    type = models.CharField(
        max_length=3,
        choices=[
            ("CL", "Casual Leave"),
            ("RH", "Recreational Holiday"),
            ("SCL", "Special Casual Leave"),
            ("EL", "Earned Leave"),
            ("VL", "Vacation Leave"),
            ("COL", "Compensatory Off Leave"),
        ],
    )

    def __str__(self):
        return self.type


class LeaveBalance(models.Model):
    employee = models.ForeignKey(User, on_delete=models.CASCADE)
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE)
    balance = models.IntegerField()

    def __str__(self):
        return f"{self.employee.username} - {self.leave_type.type} Balance: {self.balance}"


class LeaveApplication(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("APPROVED", "Approved"),
        ("REJECTED", "Rejected"),
        ("WITHDRAWN", "Withdrawn"),
        ("CANCELLED", "Cancelled"),
    ]
    applicant = models.ForeignKey(User, on_delete=models.CASCADE)
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    station_leave_details = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="PENDING")

    def __str__(self):
        return f"{self.applicant.username} - {self.leave_type.type} Application"


class SubstituteNomination(models.Model):
    leave_application = models.ForeignKey(LeaveApplication, on_delete=models.CASCADE)
    substitute = models.ForeignKey(User, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()

    def __str__(self):
        return (
            f"{self.leave_application.applicant.username} - "
            f"{self.leave_application.leave_type.type} Substitute Nomination"
        )
