from django.db import models

# Create your models here.

class Job(models.Model):
    job_id          = models.CharField(max_length=36)
    start_time      = models.FloatField()
    completion_time = models.FloatField(default=0.0)
    nrecord         = models.IntegerField(default=0)
    currecord       = models.IntegerField(default=0)
    status          = models.CharField(max_length=16, default="JOB_UNKNOWN")
    msg             = models.TextField()
    calculation_info= models.CharField(max_length=1024)

class Result(models.Model):
    job = models.ForeignKey(Job)
    cmp_id = models.IntegerField()
    result_json = models.TextField()

# Post-save handler for DBConfig models will update the settings.DATABASES dict
from django.db.models.signals import post_save, pre_delete, post_delete
from django.dispatch import receiver
from django.conf import settings

@receiver(pre_delete, sender=Result)
def delete_handler_results(sender, **kwargs):
    inst = kwargs.get('instance')
    print "deleting result for job: %s"%(inst.job)
    
