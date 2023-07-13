from functools import wraps
import time


class Util_Profile(object):

	def __init__(self):
		super(Util_Profile, self).__init__()

	def timefn(fn):
		@wraps(fn)
		def measure_time(*args, **kwargs):
			t1 = time.time()
			result = fn(*args, **kwargs)
			t2 = time.time()
			print("@timefn: {} took {} seconds".format(fn.__name__, t2-t1))
			return result
		return measure_time