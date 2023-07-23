class Sequence(list):
	def __init__(self, maxlen):
		self._maxlen = maxlen

	def append(self, element):
		self.__delitem__(slice(0, len(self) == self._maxlen))
		super(Sequence, self).append(element)

	def to_string(self):
		return '_'.join(self)

