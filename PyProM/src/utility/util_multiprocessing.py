from PyProM.src.utility.util_profile import Util_Profile
import copy

class Util_Multiprocessing(object):
	timefn = Util_Profile.timefn

	def __init__(self):
		super(Util_Multiprocessing, self).__init__()

	@property
	def _constructor(self):
		return Util_Multiprocessing


	@classmethod
	def join_dict(cls, output):
		for i, matrix in enumerate(output):
			if i == 0:
				result = copy.deepcopy(matrix)
			else:
				keys = result.keys()
				for ai in matrix.keys():
					# add new ai
					if ai not in keys:
						result[ai] = matrix[ai]
					else:
						for ai_val in matrix[ai].keys():
							if ai_val != 'outgoings':
								if ai_val not in result.keys():
									result[ai][ai_val] = matrix[ai][ai_val]
								else:
									result[ai][ai_val] += matrix[ai][ai_val]
							else:
								for aj in matrix[ai]['outgoings'].keys():
									if aj not in result[ai]['outgoings'].keys():
										result[ai]['outgoings'][aj] = matrix[ai]['outgoings'][aj]
									else:
										for aj_val in matrix[ai]['outgoings'][aj].keys():
											result[ai]['outgoings'][aj][aj_val] += matrix[ai]['outgoings'][aj][aj_val]
		return result