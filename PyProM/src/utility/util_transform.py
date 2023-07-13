import collections
class UtilTransform(object):
	def __init__(self):
		super(UtilTransform, self).__init__()

	def transpose_dict(self, dependency_graph):
	        transposed = dict()
	        for ai in dependency_graph:
	            for aj in dependency_graph[ai]:
	                if aj not in transposed:
	                    transposed[aj] = collections.defaultdict(list)
	                transposed[aj][ai] = dependency_graph[ai][aj]
	        return transposed