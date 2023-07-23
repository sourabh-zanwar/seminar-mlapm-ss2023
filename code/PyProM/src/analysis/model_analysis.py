import numpy as np
from scipy import stats
import math

class ModelAnalysis(object):

	def __init__(self):
		super(ModelAnalysis, self).__init__()

	def calculate_edge_attr_mean(self, transition_matrix, attr):
		for ai in transition_matrix:
			for aj in transition_matrix[ai]:
				transition_matrix[ai][aj]['duration_mean'] = np.mean(np.array(transition_matrix[ai][aj][attr]))
		return transition_matrix

	def caculate_percentile_values(self, transition_matrix, attr, edges='all', lower=10, upper=90):
		values = []
		if edges == 'all':
			for ai in transition_matrix:
				for aj in transition_matrix[ai]:
					values.append(transition_matrix[ai][aj][attr])
		else:
			for e in edges:
				ai = e[0]
				aj = e[1]
				values.append(transition_matrix[ai][aj][attr])
		values = np.array(values)
		l = np.percentile(values,lower)
		u = np.percentile(values,upper)
		return l, u

