from django.core.management.base import BaseCommand, CommandError
from server.models import Machine, Fact, Condition
from whdimport.models import *

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
            
            # Get a facter fact
            fact_name = 'macaddress_en0'
            raw_fact = Fact.objects.get(machine=machine, fact_name=fact_name)
            whd_machine.mac_address_en0 = raw_fact.fact_data
        
            whd_machine.save()
            machine_count += 1

        self.stdout.write('Successfully synced "%s" machines' % machine_count)