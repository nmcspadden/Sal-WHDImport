from django.db import models
from server.models import Machine

class Whdmachine(models.Model):
	machine = models.ForeignKey(Machine)
	serial = models.TextField(blank=True, default="")
	hostname = models.TextField(blank=True, default="")
	mac_address_en0 = models.TextField(blank=True, default="")
	productname = models.TextField(blank=True, default="")
	memorytotal = models.TextField(blank=True, default="")
	cpu = models.TextField(blank=True, default="")
	macosx_productversion = models.TextField(blank=True, default="")
	ipaddress = models.TextField(blank=True, default="")
	sp_local_host_name = models.TextField(blank=True, default="")
	macaddress_wifi = models.TextField(blank=True, default="")
	macaddress_eth = models.TextField(blank=True, default="")
	hd_total = models.TextField(blank=True, default="")
	type = models.TextField(blank=True, default="")
	memorysize = models.TextField(blank=True, default="")
	
	def __unicode__(self):
		return self.hostname
	class Meta:
		ordering = ['hostname']
