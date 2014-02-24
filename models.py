from django.db import models
from server.models import Machine

class Whdmachine(models.Model):
    machine = models.ForeignKey(Machine)
    serial = models.TextField()
    hostname = models.TextField()
    mac_address_en0 = models.TextField()
    def __unicode__(self):
        return self.hostname
    class Meta:
        ordering = ['hostname']