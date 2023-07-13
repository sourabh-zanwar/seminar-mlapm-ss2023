class Abs_set(list):
	def __init__(self, maxlen):
		self._maxlen = maxlen

	def append(self, element):
		if element in self:
			return
		self.__delitem__(slice(0, len(self) == self._maxlen))
		super(Abs_set, self).append(element)
		self = sorted(self)

	def to_string(self):
		return '_'.join(self)