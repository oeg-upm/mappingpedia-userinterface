from django.db import models
from datetime import datetime


class ExecutionProgress(models.Model):
    STATUS_CHOICES = (
        ('inprogress', 'In Progress'),
        ('success', 'Success'),
        ('fail', 'Fail'),
    )
    STATUS_INPROGRESS = 'inprogress'
    STATUS_SUCCESS = 'success'
    STATUS_FAIL = 'fail'
    status = models.CharField(max_length=50, choices=STATUS_CHOICES)
    user = models.CharField(max_length=250)
    timestamp = models.DateTimeField(default=datetime.now())
    result_url = models.URLField(max_length=250, default='')


