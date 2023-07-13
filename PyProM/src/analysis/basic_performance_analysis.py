import numpy as np
from scipy import stats
import math

class BPA(object):

	def __init__(self):
		super(BPA, self).__init__()

	def calculate_execution_time(self, eventlog, unit='hour'):
		execution_times = []
		caseid = eventlog.get_first_caseid()
		count = 0

		for instance in eventlog.itertuples():
			index = instance.Index
			if index == 0:
				execution_times.append(float('nan'))
				continue
			previous_caseid = eventlog.get_caseid_by_index(index-1)
			if instance.CASE_ID == previous_caseid:
				execution_time = eventlog.get_timestamp_by_index(index) - eventlog.get_timestamp_by_index(index-1)
				execution_time = divmod(execution_time.days * 86400 + execution_time.seconds, 86400)
				if unit == 'hour':
					execution_time = 24*execution_time[0] + execution_time[1]/(60*60)
				if unit == 'day':
					execution_time = execution_time[0] + execution_time[1]/(60*60*24)
				execution_times.append(execution_time)
				count = 1
			else:
				execution_times.append(float('nan'))
		eventlog = eventlog.assign(execution_time = execution_times)
		return eventlog

	def calculate_relative_time(self, eventlog, unit = 'day'):
		self.calculate_execution_time(eventlog, unit)
		relative_times = []
		for instance in eventlog.itertuples():
			index = instance.Index
			if math.isnan(instance.execution_time):
				relative_time = 0
			else:
				relative_time = relative_times[index-1] + instance.execution_time
			relative_times.append(relative_time)
		eventlog = eventlog.assign(relative_time = relative_times)
		return eventlog

	def analyze_performance(self, eventlog, value = 'execution_time', metric = 'mean', *args, **kwargs):
		if 'dim_1' in kwargs:
			dim_1 = kwargs['dim_1']
		if 'dim_2' in kwargs:
			dim_2 = kwargs['dim_2']
		if 'value' in kwargs:
			value = kwargs['value']
		if metric == 'mean':
			result = eventlog.groupby([dim_1,dim_2])[value].mean()
		if metric == 'median':
			result = eventlog.groupby([dim_1,dim_2])[value].median()
		if metric == 'min':
			result = eventlog.groupby([dim_1,dim_2])[value].min()
		if metric == 'max':
			result = eventlog.groupby([dim_1,dim_2])[value].max()
		if metric == 'std':
			result = eventlog.groupby([dim_1,dim_2])[value].std()
		if metric == 'frequency':
			result = eventlog.groupby([dim_1,dim_2])[value].count()
		if metric == 'frequency_per_case':
			result = eventlog.groupby([dim_1,dim_2])[value].count()/len(eventlog.get_caseids())

		return result

	def duplicate_event_count(self, eventlog, event):
		columns = list(eventlog.columns)
		columns.remove(event)
		columns.remove('CASE_ID')
		ref = columns[0]
		event_count = eventlog.groupby(['CASE_ID', event])[ref].count()
		#event_count = event_count.rename(columns={ref:'count'})
		return event_count
