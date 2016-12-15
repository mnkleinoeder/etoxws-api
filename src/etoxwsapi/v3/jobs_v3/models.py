from django.db import models
from django.db.models.deletion import CASCADE

class Job(models.Model):
    job_id          = models.CharField(max_length=36)
    start_time      = models.FloatField()
    completion_time = models.FloatField(default=0.0)
    nrecord         = models.IntegerField(default=0)
    currecord       = models.IntegerField(default=0)
    status          = models.CharField(max_length=16, default="JOB_UNKNOWN")
    msg             = models.TextField()
    calculation_info= models.TextField()
    pid             = models.IntegerField(default=-1)

class Result(models.Model):
    job = models.ForeignKey(Job, on_delete=CASCADE)
    cmp_id = models.IntegerField()
    result_json = models.TextField()

