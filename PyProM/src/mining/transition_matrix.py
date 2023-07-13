import sys
import os
#sys.path.append(os.path.abspath("../data"))
from PyProM.src.data.Eventlog import Eventlog
from PyProM.src.data.xes_reader import XesReader
from PyProM.src.data.sequence import Sequence
from PyProM.src.data.abs_set import Abs_set

import pandas as pd
import numpy as np
import collections
from copy import deepcopy

from multiprocessing import Process, Manager, Queue

#sys.path.append(os.path.abspath("../utility"))
from PyProM.src.utility.util_profile import Util_Profile
from PyProM.src.utility.util_multiprocessing import Util_Multiprocessing

timefn = Util_Profile.timefn



class TransitionMatrix(object):
	"""docstring for TransitionMatrix"""
	def __init__(self):
		super(TransitionMatrix, self).__init__()

	def get_transition_matrix(self, eventlog, workers, abs_type='sequence', horizon=1, target = 'Activity', name='transition_matrix'):
		self.type = abs_type
		self.horizon = horizon
		self.target = target
		self.name = name

		output = eventlog.parallelize(self._produce_transition_matrix, workers, self.type, self.horizon, target)

		transition_matrix = Util_Multiprocessing.join_dict(output)
		#print(transition_matrix)
		return transition_matrix



	@timefn
	def _produce_transition_matrix(self, eventlog, x, type = 'sequence', horizon = 1, target='Activity'):
		print("produce transition matrix")
		transition_matrix = collections.OrderedDict()
		transition_matrix['START'] = collections.OrderedDict()
		transition_matrix['START']['outgoings'] = collections.OrderedDict()

		event_trace = eventlog.get_event_trace(1, target)
		for trace in event_trace.values():
			if type == 'sequence':
				ai = Sequence(horizon)
			if type == 'set':
				ai = Abs_set(horizon)
			count = 0
			#add 'START'
			ai.append('START')
			for index, act in enumerate(trace):
				if count != 0:
					ai = deepcopy(aj)
				aj = deepcopy(ai)
				aj.append(act)
				ai_string = ai.to_string()
				aj_string = aj.to_string()
				if ai_string not in transition_matrix:
					transition_matrix[ai_string] = collections.OrderedDict()
					transition_matrix[ai_string]['outgoings'] = collections.OrderedDict()
				if aj_string not in transition_matrix[ai_string]['outgoings']:
					transition_matrix[ai_string]['outgoings'][aj_string] = collections.defaultdict(list)
					transition_matrix[ai_string]['outgoings'][aj_string]['count'] = 0
				transition_matrix[ai_string]['outgoings'][aj_string]['count'] += 1
				count = 1
				#add 'END'
				if index == len(trace) - 1:
					ai = deepcopy(aj)
					ai_string = ai.to_string()
					aj_string = 'END'
					if ai_string not in transition_matrix:
						transition_matrix[ai_string] = collections.OrderedDict()
						transition_matrix[ai_string]['outgoings'] = collections.OrderedDict()
					if aj_string not in transition_matrix[ai_string]['outgoings']:
						transition_matrix[ai_string]['outgoings'][aj_string] = collections.defaultdict(list)
						transition_matrix[ai_string]['outgoings'][aj_string]['count'] = 0
					transition_matrix[ai_string]['outgoings'][aj_string]['count'] += 1

		print("Finish")
		x.append(transition_matrix)

	def annotate_transition_matrix(self, eventlog, workers, transition_matrix, value = 'duration', start_time='default', complete_time='default'):

		output = eventlog.parallelize(self._new_annotate_transition_matrix, workers, transition_matrix,value,start_time, complete_time)

		transition_matrix = Util_Multiprocessing.join_dict(output)
		#annotate 진행하게 되면 기존에 산출했던 count가 workers 수만큼 곱해지게 됨 따라서 이를 리셋할 필요가 있음
		for ai in transition_matrix:
			for aj in transition_matrix[ai]['outgoings']:
				transition_matrix[ai]['outgoings'][aj]['count'] = transition_matrix[ai]['outgoings'][aj]['count']/workers
		return transition_matrix

	def clear_annotation(self, transition_matrix, label):
		temp_tm = deepcopy(transition_matrix)
		for ai in temp_tm:
			temp_tm[ai][label] = 0
			for aj in temp_tm[ai]['outgoings']:
				temp_tm[ai]['outgoings'][aj][label] = 0
		return temp_tm

	@timefn
	def _new_annotate_transition_matrix(self, eventlog, x, transition_matrix, value='duration', start_time='default', complete_time='default'):
		print("produce annotated transition matrix")

		#start node
		next_caseid = eventlog.get_first_caseid()
		first = True
		event_count = 0
		skip_count = 0
		for row in eventlog.itertuples():
			index = row.Index
			if index == eventlog.count_event() - 1:
				continue

			next_caseid = eventlog.get_caseid_by_index(index+1)

			#start와 현재 row 사이의 값을 annotation
			if first == True:
				if self.type == 'sequence':
					ai = Sequence(self.horizon)
				if self.type == 'set':
					ai = Abs_set(self.horizon)
				ai.append('START')
				aj = deepcopy(ai)
				if self.target == 'Activity':
					aj.append(eventlog.get_activity_by_index(index))
				elif self.target == 'RESOURCE':
					aj.append(eventlog.get_resource_by_index(index))

				ai_string = ai.to_string()
				aj_string = aj.to_string()

				#skip annotating values if ai and aj not in the transition system
				if ai_string not in transition_matrix or aj_string not in transition_matrix or aj_string not in transition_matrix[ai_string]['outgoings']:
					skip_count+=1

				else:
					if value == 'CASE_ID':
						pass
					elif value == 'processing':
						if 'processing' not in transition_matrix[aj_string]:
							transition_matrix[aj_string]['processing'] = list()

						if 'processing' not in transition_matrix[ai_string]['outgoings'][aj_string]:
							transition_matrix[ai_string]['outgoings'][aj_string]['processing'] = list()

						if start_time != 'default' and complete_time != 'default':
							#현재 index 값을 추가
							processing = eventlog.get_col_value_by_index(complete_time,index) - eventlog.get_col_value_by_index(start_time, index)
						else:
							raise("START & COMPLETE Column name should be provided to calculate processing time")
						if processing < pd.Timedelta(0):
							processing = pd.Timedelta(0)
						transition_matrix[aj_string]['processing'].append(processing)
						event_count += 1
						transition_matrix[ai_string]['outgoings'][aj_string]['processing'].append(processing)

					elif value == 'waiting':
						pass

					elif value == 'sojourn':
						if start_time == 'default':
							pass
						#start와 현재 row 사이의 sojourn은 processing과 같음 (waiting=0), if there is start time
						else:
							if 'sojourn' not in transition_matrix[aj_string]:
								transition_matrix[aj_string]['sojourn'] = list()

							if 'sojourn' not in transition_matrix[ai_string]['outgoings'][aj_string]:
								transition_matrix[ai_string]['outgoings'][aj_string]['sojourn'] = list()

							sojourn = eventlog.get_col_value_by_index(complete_time,index) - eventlog.get_col_value_by_index(start_time, index)
							if sojourn < pd.Timedelta(0):
								sojourn = pd.Timedelta(0)
							transition_matrix[aj_string]['sojourn'].append(sojourn)
							event_count += 1
							transition_matrix[ai_string]['outgoings'][aj_string]['sojourn'].append(sojourn)
				first = False

			#현재 row와 다음 row 사이의 값을 annotation, if next row has the same caseid
			if row.CASE_ID == next_caseid:
				if index == eventlog.count_event() - 2:
					break
				ai = deepcopy(aj)
				if self.target == 'Activity':
					aj.append(eventlog.get_activity_by_index(index+1))
				elif self.target == 'RESOURCE':
					aj.append(eventlog.get_resource_by_index(index+1))

				ai_string = ai.to_string()
				aj_string = aj.to_string()

				#skip annotating values if ai and aj not in the transition system
				if ai_string not in transition_matrix or aj_string not in transition_matrix or aj_string not in transition_matrix[ai_string]['outgoings']:
					skip_count+=1

				else:
					if value == 'CASE_ID':
						if 'case' not in transition_matrix[ai_string]['outgoings'][aj_string]:
							transition_matrix[ai_string]['outgoings'][aj_string]['case'] = []

						if next_caseid not in transition_matrix[ai_string]['outgoings'][aj_string]['case']:
							transition_matrix[ai_string]['outgoings'][aj_string]['case'].append(caseid)

					elif value == 'processing':
						if 'processing' not in transition_matrix[aj_string]:
							transition_matrix[aj_string]['processing'] = list()
						if 'processing' not in transition_matrix[ai_string]['outgoings'][aj_string]:
							transition_matrix[ai_string]['outgoings'][aj_string]['processing'] = list()
						if start_time != 'default' and complete_time != 'default':
							processing = eventlog.get_col_value_by_index(complete_time,index+1) - eventlog.get_col_value_by_index(start_time, index+1)
						else:
							raise("START & COMPLETE Column name should be provided to calculate processing time")
						if processing < pd.Timedelta(0):
							processing = pd.Timedelta(0)
						transition_matrix[aj_string]['processing'].append(processing)
						event_count += 1
						transition_matrix[ai_string]['outgoings'][aj_string]['processing'].append(processing)

					elif value == 'waiting':
						if 'waiting' not in transition_matrix[aj_string]:
							transition_matrix[aj_string]['waiting'] = list()
						if 'waiting' not in transition_matrix[ai_string]['outgoings'][aj_string]:
							transition_matrix[ai_string]['outgoings'][aj_string]['waiting'] = list()
						if start_time != 'default' and complete_time != 'default':
							waiting = eventlog.get_col_value_by_index(start_time,index+1) - eventlog.get_col_value_by_index(complete_time, index)
						else:
							raise("START & COMPLETE Column name should be provided to calculate waiting time")
						if waiting < pd.Timedelta(0):
							waiting = pd.Timedelta(0)
						transition_matrix[aj_string]['waiting'].append(waiting)
						event_count += 1
						transition_matrix[ai_string]['outgoings'][aj_string]['waiting'].append(waiting)

					elif value == 'sojourn':
						if 'sojourn' not in transition_matrix[aj_string]:
							transition_matrix[aj_string]['sojourn'] = list()
						if 'sojourn' not in transition_matrix[ai_string]['outgoings'][aj_string]:
							transition_matrix[ai_string]['outgoings'][aj_string]['sojourn'] = list()
						if complete_time != 'default':
							sojourn = eventlog.get_timestamp_by_index(index+1) - eventlog.get_timestamp_by_index(index)
						else:
							raise("COMPLETE Column name should be provided to calculate waiting time")
						if sojourn < pd.Timedelta(0):
							sojourn = pd.Timedelta(0)
						event_count += 1
						transition_matrix[aj_string]['sojourn'].append(sojourn)
						transition_matrix[ai_string]['outgoings'][aj_string]['sojourn'].append(sojourn)

					elif value== 'Cluster':
						if 'Cluster' not in transition_matrix[ai_string]['outgoings'][aj_string]:
							transition_matrix[ai_string]['outgoings'][aj_string]['Cluster'] = list()
						cluster = eventlog.get_col_value_by_index('Cluster',index+1)
						transition_matrix[ai_string]['outgoings'][aj_string]['Cluster'].append(cluster)

			#case의 마지막 event와 END 사이의 값을 annotation
			else:
				#add 'END'
				ai = deepcopy(aj)
				if self.type == 'sequence':
					aj = Sequence(self.horizon)
				if self.type == 'set':
					aj = Abs_set(self.horizon)
				aj.append('END')
				ai_string = ai.to_string()
				aj_string = aj.to_string()
				if ai_string not in transition_matrix and aj_string not in transition_matrix[ai_string]['outgoings']:
					skip_count+=1
				else:
					if value == 'CASE_ID':
						if 'case' not in transition_matrix[ai_string]['outgoings'][aj_string]:
							transition_matrix[ai_string]['outgoings'][aj_string]['case'] = []

						if next_caseid not in transition_matrix[ai_string]['outgoings'][aj_string]['case']:
							transition_matrix[ai_string]['outgoings'][aj_string]['case'].append(caseid)
				first = True

		print("Len of eventlog: {}".format(len(eventlog)))
		print("Event count: {}".format(event_count))
		print("Skip count: {}".format(skip_count))

		x.append(transition_matrix)
		return event_count







