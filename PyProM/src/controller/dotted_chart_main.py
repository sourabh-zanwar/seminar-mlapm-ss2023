

import sys
import os
import signal
import pandas as pd
sys.path.append(os.path.abspath(("../../../")))
from PyProM.src.data.Eventlog import Eventlog
from PyProM.src.data.xes_reader import XesReader

from PyProM.src.analysis.basic_performance_analysis import BPA

from PyProM.src.preprocessing.filter import Filter

from PyProM.src.model.fsm import FSM_Miner

from PyProM.src.visualization.chart_visualization import ChartVisualizer
import multiprocessing



if __name__ == '__main__':
	eventlog = Eventlog.from_txt('/Users/GYUNAM/Documents/example/repairExample.txt')
	eventlog = eventlog.assign_caseid('Case ID')
	eventlog = eventlog.assign_activity('Activity')
	eventlog = eventlog.assign_resource('Resource')
	eventlog = eventlog.assign_timestamp('Complete Timestamp')
	eventlog = eventlog.clear_columns()

	filter = Filter()

	eventlog = filter.remove_duplicate(eventlog)

	Bpa = BPA()

	eventlog = Bpa.calculate_execution_time(eventlog)
	eventlog = Bpa.calculate_relative_time(eventlog)

	CV = ChartVisualizer()
	CV.produce_dotted_chart(eventlog, x='TIMESTAMP', y='CASE_ID', _type = 'ACTIVITY', _time = 'actual')
