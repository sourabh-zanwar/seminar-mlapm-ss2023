

class Filter(object):
	def __init__(object):
		pass

	def remove_duplicate(self, eventlog):
		print("##remove duplicates, {}".format(len(eventlog)))
		print("# cases: {}".format(eventlog.count_case()))
		eventlog = eventlog.drop_duplicates()
		eventlog = eventlog.reset_index(drop=True)
		print("result: {}".format(len(eventlog)))
		print("# cases: {}".format(eventlog.count_case()))
		return eventlog

	#특정 column의 특정 value를 포함하는 row를 삭제함
	def remove_col_value(self, eventlog, col, value):
		print("##remove {} column's {}".format(col, value))
		print("previous # events: {}".format(len(eventlog)))
		print("previous # cases: {}".format(eventlog.count_case()))
		eventlog = eventlog.loc[eventlog[col]!=value]
		print("current # events: {}".format(len(eventlog)))
		print("current # cases: {}".format(eventlog.count_case()))
		return eventlog