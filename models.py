from django.db import models
from server.models import Machine

class Whdmachine(models.Model):
	machine = models.ForeignKey(Machine)
	serial = models.TextField(null=True)
	hostname = models.TextField(null=True)
	mac_address_en0 = models.TextField(blank=True, null=True)
	productname = models.TextField(null=True)
	memorytotal = models.TextField(null=True)
	cpu = models.TextField(null=True)
	macosx_productversion = models.TextField(null=True)
	ipaddress = models.TextField(null=True)
	sp_local_host_name = models.TextField(null=True)
	macaddress_wifi = models.TextField(blank=True, null=True)
	macaddress_eth = models.TextField(blank=True, null=True)
	hd_total = models.TextField(null=True)
	type = models.TextField(null=True)
	
	def __unicode__(self):
		return self.hostname
	class Meta:
		ordering = ['hostname']
