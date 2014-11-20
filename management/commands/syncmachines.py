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
		suffixes=['KB','MB','GB','TB']
		suffixIndex = 0
		while size > 1024:
			suffixIndex += 1 #increment the index of the suffix
			size = size/1024.0 #apply the division
		return "%.*f %s"%(precision,size,suffixes[suffixIndex])
	
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
			whd_machine.hd_total = self.GetHumanReadable(int(machine.hd_total))

			# Get the desired facts
			
			# Get the total amount of RAM ("x.xx in GB")
			fact_name = 'memorytotal'
			try:
				raw_fact = Fact.objects.get(machine=machine,fact_name=fact_name)
				whd_machine.memorytotal = raw_fact.fact_data
			except Fact.DoesNotExist:
				print whd_machine.serial + " " + fact_name + " doesn't exist."
			
			# Get the CPU type & clock speed
			fact_name = 'sp_cpu_type'
			try:
				raw_fact = Fact.objects.get(machine=machine,fact_name=fact_name)
			except Fact.DoesNotExist:
				print whd_machine.serial + " " + fact_name + " doesn't exist."
			fact_name = 'sp_current_processor_speed'
			try:
				raw_fact2 = Fact.objects.get(machine=machine,fact_name=fact_name)
				whd_machine.cpu = raw_fact.fact_data + " " + raw_fact2.fact_data
			except Fact.DoesNotExist:
				print whd_machine.serial + " " + fact_name + " doesn't exist."

			# Get the installed version of OS X
			fact_name = 'macosx_productversion'
			try:
				raw_fact = Fact.objects.get(machine=machine,fact_name=fact_name)
				whd_machine.macosx_productversion = raw_fact.fact_data
			except Fact.DoesNotExist:
				print whd_machine.serial + " " + fact_name + " doesn't exist."

			# Get the IP address of the primary interface 
			# If both ethernet and wifi are connected, it will pick first in the service order
			fact_name = 'ipaddress'
			try:
				raw_fact = Fact.objects.get(machine=machine,fact_name=fact_name)
				whd_machine.ipaddress = raw_fact.fact_data
			except Fact.DoesNotExist:
				print whd_machine.serial + " " + fact_name + " doesn't exist."

			# Get the Sharing computer name.
			fact_name = 'sp_local_host_name'
			try:
				raw_fact = Fact.objects.get(machine=machine,fact_name=fact_name)
				whd_machine.sp_local_host_name = raw_fact.fact_data
			except Fact.DoesNotExist:
				print whd_machine.serial + " " + fact_name + " doesn't exist."

			# Model of the device
			fact_name = 'productname'
			try:
				raw_fact = Fact.objects.get(machine=machine,fact_name=fact_name)
				productname = raw_fact.fact_data #not committing to whd_machine yet
			except Fact.DoesNotExist:
				print whd_machine.serial + " " + fact_name + " doesn't exist."
			if mms_available:
				# If we have MacModelShelf, then we can pull it based on the serial number.
				print "Serial: " + whd_machine.serial
				whd_machine.productname = macmodelshelf.model(macmodelshelf.model_code(whd_machine.serial).encode()).encode()
			else:
				# Otherwise, just use the productname pulled from the fact.
				whd_machine.productname = productname

			# "MAC address" should always correspond to wifi in WHD, so here are the special cases
			if "Air" in whd_machine.productname:
				fact_name = 'macaddress_en0'
				try:
					raw_fact = Fact.objects.get(machine=machine,fact_name=fact_name)
					whd_machine.macaddress_wifi = raw_fact.fact_data
					whd_machine.macaddress_eth = ""
				except Fact.DoesNotExist:
					print whd_machine.serial + " " + fact_name + " doesn't exist."
			elif "Retina" in whd_machine.productname:
				fact_name = 'macaddress_en0'
				try:
					raw_fact = Fact.objects.get(machine=machine,fact_name=fact_name)
					whd_machine.macaddress_wifi = raw_fact.fact_data
					whd_machine.macaddress_eth = ""
				except Fact.DoesNotExist:
					print whd_machine.serial + " " + fact_name + " doesn't exist."
			elif "Mac Pro" in whd_machine.productname:
				fact_name = 'macaddress_en0'
				try:
					raw_fact = Fact.objects.get(machine=machine,fact_name=fact_name)
				except Fact.DoesNotExist:
					print whd_machine.serial + " " + fact_name + " doesn't exist."
				whd_machine.macaddress_wifi = raw_fact.fact_data
				fact_name = 'macaddress_en1'
				try:
					raw_fact = Fact.objects.get(machine=machine,fact_name=fact_name)
				except Fact.DoesNotExist:
					print whd_machine.serial + " " + fact_name + " doesn't exist."
				whd_machine.macaddress_eth = raw_fact.fact_data
			else:
				fact_name = 'macaddress_en0'
				try:
					raw_fact = Fact.objects.get(machine=machine,fact_name=fact_name)
					whd_machine.macaddress_eth = raw_fact.fact_data
				except Fact.DoesNotExist:
					print whd_machine.serial + " " + fact_name + " doesn't exist."
				fact_name = 'macaddress_en1'
				try:
					raw_fact2 = Fact.objects.get(machine=machine,fact_name=fact_name)
					whd_machine.macaddress_wifi = raw_fact2.fact_data
				except Fact.DoesNotExist:
					print whd_machine.serial + " " + fact_name + " doesn't exist."				
			
			# Set the Asset Type to "Laptop" or "Desktop" depending
			if "Book" in whd_machine.productname:
				whd_machine.type = "Laptop"
			else:
				whd_machine.type = "Desktop"
			
			whd_machine.save()
			machine_count += 1

		self.stdout.write('Successfully synced "%s" machines' % machine_count)