import datetime
import xml.etree.ElementTree as ET
import collections

class XesReader(object):
	"""docstring for XesReader"""
	def __init__(self, filepath):
		super(XesReader, self).__init__()
		#filepath = './example/financial_log.xes'
		self.tree = ET.parse(filepath)
		self.root = self.tree.getroot()
		#need to specify
		self.ns = {'xes': "http://code.deckfour.org/xes"}

	def to_dict_eventlog(self, *args):
		len_attr = len(args)
		dict_eventlog= collections.defaultdict(list)

		for trace in self.root.findall('xes:trace', self.ns):
			caseid = ''
			for string in trace.findall('xes:string', self.ns):
				if string.attrib['key'] == 'concept:name':
					caseid = string.attrib['value']


			for event in trace.findall('xes:event', self.ns):
				task = ''
				user = ''
				event_type = ''
				dict_eventlog['CASE_ID'].append(caseid)
				for string in event.findall('xes:string', self.ns):
					if string.attrib['key'] == 'concept:name':
						task = string.attrib['value']

					if string.attrib['key'] == 'org:resource':
						user = string.attrib['value']

					if string.attrib['key'] == 'lifecycle:traself.nsition':
						event_type = string.attrib['value']


					#to coself.nsider additional attributes
					for i in range(len_attr):
						attr = string.attrib['value']
						dict_eventlog[args[i]].append(attr)
				dict_eventlog['ACTIVITY'].append(task)
				dict_eventlog['RESOURCE'].append(user)
				dict_eventlog['LIFECYCLE'].append(event_type)


				timestamp = ''
				for date in event.findall('xes:date', self.ns):
					if date.attrib['key'] == 'time:timestamp':
						timestamp = date.attrib['value']
						timestamp = datetime.datetime.strptime(timestamp[:-10], '%Y-%m-%dT%H:%M:%S')
				dict_eventlog['TIMESTAMP'].append(timestamp)
		print("CASE_ID len: {}".format(len(dict_eventlog['CASE_ID'])))
		print("ACTIVITY len: {}".format(len(dict_eventlog['ACTIVITY'])))
		print("RESOURCE len: {}".format(len(dict_eventlog['RESOURCE'])))
		print("LIFECYCLE len: {}".format(len(dict_eventlog['LIFECYCLE'])))
		print("TIMESTAMP len: {}".format(len(dict_eventlog['TIMESTAMP'])))

		return dict_eventlog, args

	def to_eventlog(self, _input):
		return Eventlog.from_dict(_input)


if __name__ == '__main__':
	XR = XesReader('./example/financial_log.xes')
	dict_eventlog, attrs = XR.to_dict_eventlog()
	eventlog = XR.to_eventlog(dict_eventlog)
	print(eventlog)


