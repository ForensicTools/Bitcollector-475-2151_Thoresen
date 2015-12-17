####
## This module is for harvesting logs from Skype, AIM, MSN Messenger,
## and other chat apps
####
import os, sys, time, json, loggin

_module_version = "ChatHarvest v0.0.1"

class ModuleSettings():
	def __init__(self, module):
		for key in module:
			if (key == "name"):
				self.name == module[key]
			elif (key == "parameters"):
					for param, value in param_pair.iteritems():
						if (param == "Lucases"):
							print "Lucases detected! => " + value
