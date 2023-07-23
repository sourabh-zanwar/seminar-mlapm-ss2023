import pandas as pd
import numpy as np
import multiprocessing
from multiprocessing import Process, Manager, Queue
import math

from PyProM.src.data.importing import Import

import sys
import os
from PyProM.src.utility.util_profile import Util_Profile
from PyProM.src.utility.util_multiprocessing import Util_Multiprocessing
import time
from functools import wraps

def timefn(fn):
	@wraps(fn)
	def measure_time(*args, **kwargs):
		t1 = time.time()
		result = fn(*args, **kwargs)
		t2 = time.time()
		print("@timefn: {} took {} seconds".format(fn.__name__, t2-t1))
		return result
	return measure_time


timefn = Util_Profile.timefn
class Eventlog(pd.DataFrame):
	"""docstring for Eventlog"""
	def __init__(self, *args, **kwargs):
		super(Eventlog, self).__init__(*args, **kwargs)
		self._columns = []


	@property
	def _constructor(self):
		return Eventlog

	@classmethod
	def from_xes(cls, path):
		_import = Import(path, format='xes')
		dict_eventlog = _import.eventlog
		if isinstance(dict_eventlog, dict):
			print("import dict and produce eventlog")
			df =  Eventlog.from_dict(dict_eventlog)
			return df

	@classmethod
	def from_txt(cls, path, sep='\t', encoding=None, **kwargs):
		if 'dtype' in kwargs:
			dtype = kwargs['dtype']
		else:
			dtype = None
		if 'index_col' in kwargs:
			index_col = kwargs['index_col']
		else:
			index_col=False
		df = pd.read_csv(path, sep = sep, index_col = index_col, dtype=dtype, encoding=encoding)
		return Eventlog(df)

	"""
	def __call__(self, path, format='xes'):
		if format == 'xes':
			_import = Import(path, format='xes')
			dict_eventlog = _import.eventlog
			return self.dict_to_dataframe(dict_eventlog)

		if format == 'txt':
			return self.csv_to_dataframe(path)
	"""
	@timefn
	def assign_caseid(self, *args):
		count = 0
		for arg in args:
			if count == 0:
				self['CASE_ID'] = self[arg].apply(str)
			else:
				self['CASE_ID'] += '_' + self[arg].apply(str)
			#del self[arg]
			count +=1
		self._columns.append('CASE_ID')
		return self

	@timefn
	def assign_activity(self, *args):
		count = 0
		for arg in args:
			if count == 0:
				self['Activity'] = self[arg].apply(str)
			else:
				self['Activity'] += '_' + self[arg].apply(str)
			#del self[arg]
			count +=1
		self._columns.append('Activity')
		return self

	@timefn
	def assign_resource(self, *args):
		count = 0
		for arg in args:
			if count == 0:
				self['Resource'] = self[arg].astype(str)
			else:
				self['Resource'] += '_' + self[arg].astype(str)
			#del self[arg]
			count +=1
		self._columns.append('Resource')
		return self

	@timefn
	def assign_timestamp(self, name, new_name = 'TIMESTAMP', _format = '%Y/%m/%d %H:%M:%S', errors='ignore'):
		print(_format)
		self[name] = pd.to_datetime(self[name], format = _format, errors=errors)
		self.rename(columns={name: new_name}, inplace=True)
		#self.loc[pd.isna(self[name]),name] = '-'
		self._columns.append(new_name)
		return self

	def assign_attr(self, **kwargs):
		"""
		이 함수는, ~~~~다.
		#할일: 컬럼명만 바꾸는 것으로!
		:param kwargs: old_col=데이터에 포함된 컬럼명,  new_col=생성한 이벤트로그에 지정할 컬럼명
		:return: 이벤트로그
		"""
		if 'old_col' in kwargs:
			old_col = kwargs['old_col']
		if 'new_col' in kwargs:
			new_col = kwargs['new_col']
		else:
			new_col = kwargs['old_col']
		self[new_col] = self[old_col]
		self._columns.append(new_col)
		del self[old_col]
		self._columns.append(new_col)
		return self

	def assign_cluster(self, *args):
		count = 0
		for arg in args:
			if count == 0:
				self['Cluster'] = self[arg].astype(str)
			else:
				self['Cluster'] += '_' + self[arg].astype(str)
			#del self[arg]
			count +=1
		self._columns.append('Cluster')
		return self

	def sort(self, by=['CASE_ID']):
		self = self.sort_values(by)
		return self

	def clear_columns(self, *args, **kwargs):
		if 'extra' in kwargs:
			extra = kwargs['extra']
		else:
			extra = []
		self = self[self._columns]
		return self



	def join_columns(self, col_name, *args):
		if len(args) < 2:
			print("join_columns requires at least 2 columns")
		count = 0
		tmp = self.copy(deep=True)
		for arg in args:
			if count == 0:
				self[col_name] = tmp[arg].astype(str)
			else:
				self[col_name] += '/' + tmp[arg].astype(str)
			#del self[arg]
			count +=1
		return self

	"""
	utility functions
	"""
	def get_event_trace(self, workers, value = 'Activity'):
		output = self.parallelize(self._get_event_trace, workers, value)
		event_trace = Util_Multiprocessing.join_dict(output)
		return event_trace

	def _get_event_trace(self, eventlog, x, value='Activity'):
		event_trace = dict()
		count = 0
		for instance in eventlog.itertuples():
			index = instance.Index
			if value == 'Activity':
				ai = eventlog.get_activity_by_index(index)
			elif value == 'Resource':
				ai = eventlog.get_resource_by_index(index)
			elif value == 'TIMESTAMP':
				ai = eventlog.get_timestamp_by_index(index)
			else:
				ai = eventlog.get_col_value_by_index(value, index)
			if index == 0:
				event_trace[instance.CASE_ID] = [ai]
				continue

			caseid = eventlog.get_caseid_by_index(index-1)

			if instance.CASE_ID == caseid:
				event_trace[instance.CASE_ID].append(ai)

			else:
				event_trace[instance.CASE_ID] = [ai]


		#print("Finish")

		x.append(event_trace)

	def _get_trace_count(self, event_trace):
		trace_count = dict()
		traces = event_trace.values()
		for trace in traces:
			trace = tuple(trace)
			if trace not in trace_count:
				trace_count[trace] = 0
			trace_count[trace] += 1
		return trace_count


	def get_caseids(self):
		unique_caseids = self['CASE_ID'].unique()
		return unique_caseids

	def get_activities(self):
		unique_activities = self['Activity'].unique()
		return unique_activities

	def get_resources(self):
		unique_resources = self['Resource'].unique()
		return unique_resources

	def get_timestamps(self):
		unique_timestamps = self['TIMESTAMP'].unique()
		return unique_timestamps

	#특정 col의 unique한 값을 리스트 형태로 리턴
	def get_col_values(self,col):
		return list(set(self[col]))

	def get_first_caseid(self):
		return self['CASE_ID'][0]

	def get_caseid_by_index(self,index):
		return self['CASE_ID'][index]

	def get_resource_by_index(self, index):
		return self['Resource'][index]

	def get_activity_by_index(self, index):
		return self['Activity'][index]

	def get_timestamp_by_index(self, index):
		return self['TIMESTAMP'][index]

	def get_col_value_by_index(self, col, index):
		return self[col][index]

	#특정 col의 특정 value를 포함하는 row를 리턴
	def get_col_value(self, col, value):
		value_df = self.loc[self[col]==value]
		value_df.name = value
		return value_df

	def change_col_value(self, col, old_val, new_val):
		self.loc[self[col]==old_val, col] = new_val
		return self

	def col_val_to_numeric(self, col):
		"""
		To make a chart using bokeh, x values and y values must be numeric.
		Accordingly, change column values to numeric so that it can be properly drawn by bokeh

		Key arguements
		col -- column to be converted to numeric
		"""
		self.sort_values(by=col, inplace=True)
		self.reset_index(drop=True, inplace=True)
		indexs = []
		i=1
		for index, instance in self.iterrows():
			if index==0:
				indexs.append(i)
				continue
			value = self[col][index-1]
			if instance[col] != value:
				i+=1
			indexs.append(i)
		self.loc[:, 'new_col'] = indexs
		return self


	def filter(self, criterion, value):
		return self.loc[self[criterion] == value, :]

	# 특정 col에 특정 value를 포함하는 row를 삭제
	def remove_col_value(self, col, value):
		return self.loc[self[col] != value]

	#eventlog의 event 총 개수를 리턴
	def count_event(self):
		return len(self.index)

	#eventlog 내 case의 개수를 리턴
	def count_case(self):
		return len(set(self['CASE_ID']))

	#특정 col의 unique한 값의 개수를 리턴
	def count_col_values(self, col):
		return len(set(self[col]))

	#모든 col의 unique한 값의 개수를 프린트함
	def show_col_counts(self):
		columns = self.columns
		for col in columns:
			print("unique counts of {}: {}".format(col,len(set(self[col]))))

	def count_col_case(self, col):
		col_case = self.groupby(col).CASE_ID.apply(list).apply(set)
		col_case_count = col_case.apply(len)
		col_case_count_mean = np.mean(col_case_count)
		col_case_count_std = np.std(col_case_count)
		print("CLUSTER count: {}".format(col_case_count))
		print("CLUSTER count mean: {}".format(col_case_count_mean))
		print("CLUSTER count std: {}".format(col_case_count_std))
		return col_case_count

	def count_duplicate_values(self, eventlog, **kwargs):
		"""특정 값이 중복되는 경우 중복횟수의 빈도를 return함
		e.g. 1번 중복: 100, 2번 중복: 300

		Keyword arguments:
		col -- 특정 col이 중복된 것을 확인하고 싶은 경우 (default: Activity)

		"""
		if 'col' in kwargs:
			col = kwargs['col']
			traces = eventlog.get_event_trace(workers=4, value=col)
		else:
			traces = eventlog.get_event_trace(workers=4, value='Activity')
		count=0
		inv_act_counts = []
		for t in traces:
			act_count = dict(Counter(traces[t]))

			inv_act_count = dict()
			for k,v in act_count.items():
				if v < 2:
					continue
				if v in inv_act_count:
					inv_act_count[v].append(k)
				else:
					inv_act_count[v] = [k]
			inv_act_counts.append(inv_act_count)

		count_result_step = dict()
		for inv_act_count in inv_act_counts:
			for k in inv_act_count:
				if k not in count_result_step:
					count_result_step[k] = 1
				else:
					count_result_step[k] += 1

		result = pd.DataFrame(list(count_result_step.items()), columns=['repetition', 'count'])
		return result

	def count_loops(self, eventlog, **kwargs):
		"""step이 연속된 경우를 count함. Step1-->Step1인 경우 1, Step1-->Step1-->Step1인 경우 2, 동시에 동일 device에서 수행되었는지도 계산함

		Keyword arguments:
		col -- 특정 col이 중복된 것을 확인하고 싶은 경우 (default: Activity)
		value -- 특정 값이 연속된 것을 확인하고 싶은 경우 e.g. 'Null'
		"""
		if 'col' in kwargs:
			col = kwargs['col']
			traces = eventlog.get_event_trace(workers=4, value=col)
		else:
			traces = eventlog.get_event_trace(workers=4, value='Activity')
		count=0
		if 'value' in kwargs:
			value = kwargs['value']
		else:
			value = 'default'
		for t, r in zip(traces, resource_traces):
			for index, act in enumerate(traces[t]):
				if index == len(traces[t]) -1:
					continue
				if value == 'default':
						count+=1
				else:
					if act == value and traces[t][index+1] == value:
						count+=1
		print("count_consecutives: {}".format(count))
		return count


	def describe(self):
		print("# events: {}".format(len(self)))
		print("# cases: {}".format(len(set(self['CASE_ID']))))
		print("# activities: {}".format(len(set(self['Activity']))))
		print("# resources: {}".format(len(set(self['Resource']))))
		try:
			print("average yield: {}".format(np.mean(self['VALUE'])))
		except AttributeError:
			print("yield not exists")

	def split_on_case(self, split):
		caseid = self.get_caseids()
		sub_cases = []
		for d in np.array_split(caseid, split):
			sub_cases.append(d)
		sub_logs = []
		for i in range(len(sub_cases)):
			sub_log = self.loc[self['CASE_ID'].isin(sub_cases[i]), :]
			sub_log.reset_index(drop=True, inplace=True)
			sub_logs.append(sub_log)
		return sub_logs

	def parallelize(self, func, workers=multiprocessing.cpu_count(), *args):
		sublogs = self.split_on_case(workers)
		output = Queue()
		manager = Manager()
		output = manager.list()
		# Setup a list of processes that we want to run
		processes = [Process(target=func, args=(sublogs[i], output)+args) for i in range(len(sublogs))]
		# Run processes
		for p in processes:
		    p.start()

		# Exit the completed processes
		for p in processes:
			p.join()

		return output

	#Relation Dictionary(key : AfterActovoty,, value : PreActivity list)
	##You need to specify the objective of this function
	##Additionally, please try to make the code below more efficient. (Both in terms of performance and visibility)
	def relation_dictionary(self, pre_col, aft_col):
		relation_set = {}
		aft_activity_list = self.get_col_values(pre_col)
		for i in aft_activity_list:
			relation_set[i] = []
		for i in range(len(self)):
			relation_set[self[aft_col][i]].append(self[pre_col][i])

		return relation_set



if __name__ == '__main__':
	"""
	eventlog = Eventlog.from_xes('./example/running_example.xes')
	print(type(eventlog))
	"""
	eventlog = Eventlog.from_txt('/Users/GYUNAM/Desktop/LAB/SAMSUNG_PROJECT/IMPLE/input/Sample_data.txt')

	eventlog = eventlog.assign_caseid('ROOT_LOT_ID', 'WAFER_ID')
	eventlog = eventlog.assign_timestamp('TKIN_TIME', 'TKOUT_TIME')
	print(eventlog)







