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

#sys.path.append(os.path.abspath("../utility"))
from PyProM.src.mining.transition_matrix import TransitionMatrix

timefn = Util_Profile.timefn

class DependencyGraph(object):
	def __init__(self):
		super(DependencyGraph, self).__init__()

	def get_dependency_graph(self, eventlog):
		dependency_graph = self._produce_dependency_graph(eventlog)
		return dependency_graph

	def _produce_dependency_graph(self, eventlog):
		TM = TransitionMatrix()
		transition_matrix = TM.get_transition_matrix(eventlog, 1, type='sequence', horizon=1)
		dependency_graph = dict()
		for ai in transition_matrix:
			if ai not in dependency_graph:
				dependency_graph[ai] = dict()
			for aj in transition_matrix[ai]:
				if ai == aj:
					aa = transition_matrix[ai][aj]['count']
					measure = aa/(aa+1)
				else:
					ab = transition_matrix[ai][aj]['count']
					ba = 0
					if aj in transition_matrix:
						if ai in transition_matrix[aj]:
							ba = transition_matrix[aj][ai]['count']
					measure = (ab - ba)/(ab + ba + 1)
				if aj not in dependency_graph[ai]:
					dependency_graph[ai][aj] = collections.defaultdict(list)
				dependency_graph[ai][aj]['count'] = ab
				dependency_graph[ai][aj]['measure'] = measure
		return dependency_graph