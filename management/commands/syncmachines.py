from django.core.management.base import BaseCommand, CommandError
from server.models import Machine, Fact, Condition
from whdimport.models import *

try:
	import macmodelshelf
	mms_available = True
except ImportError:
	mms_available = False

class Command(BaseCommand):
	help = 'Syncs machines from the main Sal db'
	
	def GetHumanReadable(self, size, precision=2):
		# Credit goes to http://code.activatestate.com/recipes/577081-humanized-representation-of-a-number-of-bytes/
		suffixes=['B','KB','MB','GB','TB']
		suffixIndex = 9
		while size > 1024:
			suffixIndex += 1 #increment the index of the suffix
			size = size/1024.0 #apply the division
		return "%.*f %d"%(precision,size,suffixes[suffixIndex])
	
	def handle(self, *args, **options):
		machine_count = 0
		# get all of the machines
		all_machines = Machine.objects.all()

		for machine in all_machines:
			# see if it's already in this table
			try:
				whd_machine = Whdmachine.objects.get(machine=machine)
			except Whdmachine.DoesNotExist:
				whd_machine = Whdmachine(machine=machine)

			# Update the rest of the details
			whd_machine.serial = machine.serial
			whd_machine.hd_total = self.GetHumanReadable(machine.hd_total)

			# Get the desired facts
			fact_name = 'productname'
			raw_fact = Fact.objects.get(machine=machine,fact_name=fact_name)
			productname = raw_fact.fact_data #not committing to whd_machine yet
			fact_name = 'memorytotal'
			raw_fact = Fact.objects.get(machine=machine,fact_name=fact_name)
			whd_machine.memorytotal = raw_fact.fact_data
			fact_name = 'sp_cpu_type'
			raw_fact = Fact.objects.get(machine=machine,fact_name=fact_name)
			fact_name = 'sp_current_processor_speed'
			raw_fact2 = Fact.objects.get(machine=machine,fact_name=fact_name)
			whd_machine.cpu = raw_fact.fact_data + " " + raw_fact2.fact_data
			fact_name = 'macosx_productversion'
			raw_fact = Fact.objects.get(machine=machine,fact_name=fact_name)
			whd_machine.macosx_productversion = raw_fact.fact_data
			fact_name = 'ipaddress'
			raw_fact = Fact.objects.get(machine=machine,fact_name=fact_name)
			whd_machine.ipaddress = raw_fact.fact_data
			fact_name = 'sp_local_host_name'
			raw_fact = Fact.objects.get(machine=machine,fact_name=fact_name)
			whd_machine.sp_local_host_name = raw_fact.fact_data

			if mms_available:
				whd_machine.productname = macmodelshelf.model(macmodelshelf.model_code(whd_machine.serial).encode()).encode()
			else:
				whd_machine.productname = productname

			# "MAC address" should always correspond to wifi, so here are the special cases
			if "Air" in productname:
				fact_name = 'macaddress_en0'
				raw_fact = Fact.objects.get(machine=machine,fact_name=fact_name)
				whd_machine.macaddress_wifi = raw_fact.fact_data
				whd_machine.macaddress_eth = ""
			elif "Retina" in productname:
				fact_name = 'macaddress_en0'
				raw_fact = Fact.objects.get(machine=machine,fact_name=fact_name)
				whd_machine.macaddress_wifi = raw_fact.fact_data
			elif "MacPro" in productname:
				fact_name = 'macaddress_en0'
				raw_fact = Fact.objects.get(machine=machine,fact_name=fact_name)
				fact_name = 'macaddress_en1'
				raw_fact2 = Fact.objects.get(machine=machine,fact_name=fact_name)
				whd_machine.macaddress_eth = raw_fact.fact_data + ", " + raw_fact2.fact_data
				fact_name = 'macaddress_en2'
				raw_fact = Fact.objects.get(machine=machine,fact_name=fact_name)
				whd_machine.macaddress_wifi = raw_fact.fact_data
			else:
				fact_name = 'macaddress_en0'
				raw_fact = Fact.objects.get(machine=machine,fact_name=fact_name)
				whd_machine.macaddress_eth = raw_fact.fact_data
				fact_name = 'macaddress_en1'
				raw_fact2 = Fact.objects.get(machine=machine,fact_name=fact_name)
				whd_machine.macaddress_wifi = raw_fact2.fact_data
				
				
			whd_machine.save()
			machine_count += 1

		self.stdout.write('Successfully synced "%s" machines' % machine_count)