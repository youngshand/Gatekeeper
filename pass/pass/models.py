from django.db import models

class Accounts(models.Model):
	name = models.CharField(max_length = 100)
	username = models.CharField(max_length = 100)
	password = models.CharField(max_length = 100)
	url = models.CharField(max_length = 256, default='', blank=True)
	metadata = models.TextField(default='', blank=True)