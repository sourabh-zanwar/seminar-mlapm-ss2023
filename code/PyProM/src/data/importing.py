import pandas as pd
from PyProM.src.data.xes_reader import XesReader

class Import(object):
	def __init__(self, path, format='xes'):
		if format == 'xes':
			self.eventlog = self.import_xes(path)


	def import_xes(self, path):
		XR = XesReader(path)
		dict_eventlog, attrs = XR.to_dict_eventlog()
		return dict_eventlog

