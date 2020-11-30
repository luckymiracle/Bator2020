from __future__ import unicode_literals
from django.db import models
from django.forms import ModelForm

class incubation(models.Model):
    name = models.CharField(default="Batch One", max_length=len("Batch One"))
    start_date = models.DateTimeField(auto_now_add=True)
    total_days = models.IntegerField(default=21)
    stop = models.BooleanField(default=False)
    lockdown = models.IntegerField(default=18)
    RH = models.FloatField(default=65)
    def __str__(self):
        return self.name + ' ' + str(self.start_date) + ' ' + str(self.total_days)\
               + ' ' + str(self.stop) + ' ' + str(self.lockdown) + ' ' + str(self.RH)

class IncubationForm(ModelForm):
	class Meta:
		model = incubation
		fields = ['name', 'total_days', 'stop', 'lockdown', 'RH']
    
class DHT(models.Model):
    incub = models.ForeignKey(incubation, on_delete=models.CASCADE)
    temperature = models.FloatField(default=60)
    Humidity = models.FloatField(default=40)
    date_log = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return "T:"+ str(self.temperature) + " H:" + str(self.Humidity) + " " + str(self.date_log)
    
class Rotation(models.Model):
    incub = models.ForeignKey(incubation, on_delete=models.CASCADE)
    last_rotation = models.DateTimeField(auto_now_add=True)
    start_image = models.CharField(default="", max_length=254)
    end_image = models.CharField(default="", max_length=254)
    def __str__(self):
        return str(self.last_rotation)

class Email(models.Model):
    from_email = models.EmailField(max_length=100)
    from_password = models.CharField(max_length=100)
    to_email = models.EmailField(max_length=100)
    def __str__(self):
        return "From: " + self.from_email + " To: " + self.to_email

class RHT(models.Model):
    incub = models.ForeignKey(incubation, on_delete=models.CASCADE)
    ktherm_temp = models.FloatField(default=60)
    amb_temp = models.FloatField(default=60)
    rh = models.FloatField(default=60)
    inc_temp = models.FloatField(default=60)
    date_log = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return "KT:" + str(self.ktherm_temp) + " AT:" + str(self.amb_temp) + " RH:" + \
               str(self.rh) + " IT:" + str(self.inc_temp)

class Recipients(models.Model):
    add = models.BooleanField(default=False)
    address = models.EmailField(max_length=100)
    def __str__(self):
        return "add: " + str(self.add) + "to: " + str(self.address)
    
