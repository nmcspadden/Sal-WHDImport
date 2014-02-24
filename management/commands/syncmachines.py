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
			whd_machine.hostname = machine.hostname

			# Get the desired facts
			fact_name = 'macaddress_en0'
			raw_fact = Fact.objects.get(machine=machine,fact_name=fact_name)
			whd_machine.mac_address_en0 = raw_fact.fact_data
			fact_name = 'memorytotal'
			raw_fact = Fact.objects.get(machine=machine,fact_name=fact_name)
			whd_machine.memorytotal = raw_fact.fact_data
			fact_name = 'sp_cpu_type'
			raw_fact = Fact.objects.get(machine=machine,fact_name=fact_name)
			fact_name = 'sp_current_processor_speed'
			raw_fact2 = Fact.objects.get(machine=machine,fact_name=fact_name)
			whd_machine.cpu = raw_fact.fact_data + " " + raw_fact2.fact_data

			if mms_available:
				whd_machine.productname = macmodelshelf.model(macmodelshelf.model_code(whd_machine.serial).encode()).encode()
			else:
				fact_name = 'productname'
				raw_fact = Fact.objects.get(machine=machine,fact_name=fact_name)
				whd_machine.productname = raw_fact.fact_data

			whd_machine.save()
			machine_count += 1

		self.stdout.write('Successfully synced "%s" machines' % machine_count)