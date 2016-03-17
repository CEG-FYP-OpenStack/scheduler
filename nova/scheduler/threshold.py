# import time, threading
from __future__ import division
from oslo_log import log as logging
import MySQLdb


LOG = logging.getLogger(__name__)


class ThresholdManager():
	"""docstring for ThresholdManager"""

	on_demand_high = 0
	on_demand_low = 0
	spot = 0	

	def __init__(self):
		self.update_attributes()

	def get_vcpus_data(self):
		db = MySQLdb.connect("127.0.0.1","root","password","nova")
		cursor = db.cursor()
		cursor.execute("select vcpus,vcpus_used from compute_nodes")
		data = cursor.fetchall()
		vcpus = 0
		vcpus_used = 0
		for row in data:
			vcpus += row[0]
			vcpus_used += row[1]	
		LOG.debug('Virtual CPUs %(vcpus)s',{'vcpus': vcpus})
		LOG.debug('Virtual CPUs Used %(vcpus_used)s', {'vcpus_used': vcpus_used})
		db.close()
		return [vcpus, vcpus_used]

	def get_ram_data(self):
		db = MySQLdb.connect("127.0.0.1", "root", "password", "nova")
		cursor = db.cursor()
		cursor.execute("select memory_mb,memory_mb_used from compute_nodes")
		data = cursor.fetchall()
		total_ram = 0
		total_ram_used = 0

		for row in data:
			total_ram += row[0]
			total_ram_used = row[1]
		LOG.debug('Ram %(ram)s', {'ram': total_ram})
		LOG.debug('Ram used %(ram_used)s', {'ram_used': total_ram_used})
		db.close()
		return [total_ram, total_ram_used]

	def update_attributes(self):
		vcpus_data = self.get_vcpus_data()
		ram_data = self.get_ram_data()
		LOG.debug('VCPUS %(vcpus)s', {'vcpus': vcpus_data})
		vcpu_usage = vcpus_data[1]/vcpus_data[0]*100
		ram_usage = ram_data[1]/ram_data[0]*100

		total_usage = (vcpu_usage+ram_usage)/2
		LOG.debug('Total Usage %(total_usage)s', {'total_usage': total_usage})

		if total_usage < 25:
			ThresholdManager.on_demand_high = 1
			ThresholdManager.on_demand_low = 1
			ThresholdManager.spot = 1
		elif total_usage >=25 and total_usage < 82:
			ThresholdManager.on_demand_high = 1
			ThresholdManager.on_demand_low = 1
			ThresholdManager.spot = 0
		elif total_usage >=82:
			ThresholdManager.on_demand_high = 1
			ThresholdManager.on_demand_low = 0
			ThresholdManager.spot = 0

	def get_attributes(self):
		attributes = {}
		if ThresholdManager.on_demand_high == 1:
			attributes['on_demand_high'] = 1
		if ThresholdManager.on_demand_low == 1:
			attributes['on_demand_low'] = 1
		if ThresholdManager.spot == 1:
			attributes['spot'] = 1
		return attributes