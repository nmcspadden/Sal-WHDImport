WHD Bridge
==========

Massive thanks go to Graham Gilbert (https://github.com/grahamgilbert/) for developing Sal (https://github.com/grahamgilbert/sal).  It's a straightforward reporting tool to get information from the results of Munki (https://code.google.com/p/munki/) and optionally Facter (http://puppetlabs.com/facter) into a visual dashboard.

It also has a nice plugin architecture that allows for applications to use the data collected from Sal and Facter.  If you're using a MySQL database backend for Sal, you can also let other external sources access that data.

You can turn Sal into an automated asset tracking system by using Web Help Desk (http://www.webhelpdesk.com).  WHD has a free license that allows unlimited use by a single account, and can be hosted on multiple platforms.  If you've already got Sal installed on a Linux server (it provides instructions for Ubuntu and CentOS), you can easily add WHD to that platform.  

The reason to use WHD is that it supports automated discovery through a number of channels - including using the JDBC to access a MySQL database.  If you configure Sal to use a MySQL backend (anything that isn't Sqlite, really), you can automatically sync data to WHD through this discovery connection.

_Note: This may work perfectly fine with other database backends like PostGres, but I have no experience or familiarity with them and I have not tested that at all.  I've only tested this with MySQL._

Preparing Sal for WHD
---------------------

Off the bat, Sal won't work with WHD's automatic integration.  WHD only accepts a flat table view to pull data from.  Sal stores some limited information about machines in a flat database, but it stores information from Facter very differently.  Facter information goes into a table that has "fact_name" and "fact_data" as columns, and the name of the fact (such as "macaddress_en0" is obviously the content of the "fact_name" field and "fact_data" contains the corresponding information.  Because of this approach, WHD can only pull the "fact_name" or the "fact_data" and map it to a single attribute - and we don't want that because "fact_name" and "fact_data" will not be consistent.  

In other words, you can't map "fact_data" to a field like "MAC address" becaue it won't always contain MAC addresses.

So we need a flat table to work with in order to let WHD work with the data.  The awesome news is that Sal allows for plugins and applications to use its data and do other fun things with them - including make more tables in MySQL to store it in different configuration.

Graham Gilbert wrote the "whdimport" module and deserves full credit for it.  I simply added the pieces on that I wanted to be recorded in WHD.  You can add any custom fields you want into WHD, and you can map these attributes by modifying the "whdimport" app.

Installing whdimport
---------------

0. Activate the virtual env as saluser.
1. Download the repo into a "whdimport" folder in the root of sal- the end result should be /usr/local/sal_env/sal/whdimport/ which contains all of the files in this repo.
2. Add "whdimport" to the INSTALLED_APPS section of settings.py (/usr/local/sal_env/sal/sal/settings.py).
3. If you make any changes to the models (fields), you'll need to run: ```python manage.py schemamigration whdimport --auto```
4. Migrate the databases: ```python manage.py migrate whdimport```
5. Now sync the data into the new table: ```python manage.py syncmachines```

If you check MySQL, you'll see a new table called "whdimport_whdmachine".  This now contains the fields that are specified in whdimport/models.py.  The data is populated when you run syncmachines as in step 5 above.

Modifying The Models
--------------------

What fields are created is determined by the contents of models.py.  You can add new fields into the "Whdmachine" class like this:
```
fieldname = models.TextField()
```

With the field named, you'll need to populate that data, and that happens when you run syncmachines. You'll need to modify whdimport/management/commands/syncmachines.py.

The examples already demonstrate how to pull facter facts and assign them a field.  Here's the generic example where the words in CAPITALS indicate that you should replace them:
```
fact_name = 'NAME_OF_FACT_reported_by_facter'
raw_fact = Fact.objects.get(machine=machine, fact_name=fact_name)
whd_machine.FACT_NAME = raw_fact.fact_data
```
The "FACT_NAME" part in whd_machine.FACT_NAME should be identical to what you listed in models.py.  So if you want to add a field for CPU architecture, you could add "arch = models.TextField()" to models.py and then assign the value of a facter fact to it with "whd_machine.arch = raw_fact.fact_data".  The name of the fact you get must match a fact_name reported by facter, otherwise the Fact.objects.get() call will fail and report an error when you run syncmachines.

Adding custom facts to facter is outside of the scope of this article, but there's documentation about that on PuppetLab's website.  

Remember that every time you make a change to the models, you'll need to update the schema:
```
python manage.py schemamigration whdimport --auto
python manage.py migrate whdimport
python manage.py syncmachines
```

Pulling Data With WHD
---------------------

Once you've got your new table set up from whdimport, you can map them to attributes in Web Help Desk using the JDBC connector.

_Note: The JDBC connector does not come bundled with WebHelpDesk by default due to licensing issues, so you'll need to install that separately.  See http://knowledgebase.solarwinds.com/kb/questions/4182/Error+Msg%3A+Unable+to+connect+to+database for details._

Configure a new Discovery Connection in Setup - Assets - Discovery Connections.  Choose "MySQL" as the Database Type, and enter in appropriate credentials.  For "Table or View", choose "whdimport_whdmachine", as that's the table we created with whdimport that we'll be pulling data from.  Choose the "Sync Column" of your choice - I recommend using "serial", as that will try to match serial numbers from Sal into existing assets in Web Help Desk.

The Attribute Mapping is the real magic - you can assign fields you created in the whdimport models.py to fields in Web Help Desk.  You can add any number of custom fields to your assets, so this is a good way to collect any data that you're interested in harvesting.  My own example includes the Ethernet MAC address (if present), hard drive capacity, total RAM, and CPU speed and type.

Once you've got the fields mapped to your satisfaction, you can initiate a Sync and see the results in the Assets section.  Do any fine-tuning as necessary on your field mapping.  Remember that if you make any changes to the models, you'll need to adjust the syncmachines.py to properly populate it, and then migrate the schema as well.

WebHelpDesk can automate pulling data from its discovery connections, but note that the data in the "whdimport_whdmachine" table isn't updated until you run "syncmachines."  It may be useful to setup a cronjob or automated schedule for "syncmachine" runs if you want to keep this up to date.
