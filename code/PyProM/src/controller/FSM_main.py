import sys
import os
import signal
import pandas as pd
from pathlib import Path
p = Path(__file__).resolve().parents[3]
sys.path.append(os.path.abspath(str(p)))
from PyProM.src.data.Eventlog import Eventlog
from PyProM.src.data.xes_reader import XesReader

from PyProM.src.mining.transition_matrix import TransitionMatrix
from PyProM.src.mining.dependency_graph import DependencyGraph

from PyProM.src.model.fsm import FSM_Miner

from PyProM.src.visualization.svg_widget import Visualization

from PyQt5 import QtSvg,QtCore,QtGui,Qt,QtWidgets

import multiprocessing



if __name__ == '__main__':
	#eventlog
	eventlog = Eventlog.from_txt('/Users/GYUNAM/Documents/example/repairExample.txt')
	eventlog = eventlog.assign_caseid('Case ID')
	eventlog = eventlog.assign_activity('Activity')
	eventlog = eventlog.assign_resource('Resource')
	eventlog = eventlog.assign_timestamp('Complete Timestamp')
	eventlog = eventlog.clear_columns()

	#preprocessing

	#Transition Matrix
	TM = TransitionMatrix()
	transition_matrix = TM.get_transition_matrix(eventlog, 4, type='sequence', horizon=2)
	transition_matrix = TM.annotate_transition_matrix(eventlog, 4, transition_matrix)

	#FSM model
	fsm = FSM_Miner()
	fsm_graph = fsm._create_graph(transition_matrix)
	fsm.get_graph_info(fsm_graph)
	dot = fsm.get_dot(fsm_graph)
	#Visualizer
	app = QtWidgets.QApplication(sys.argv)

	window = Visualization()
	window.show()

	#for path in app.arguments()[1:]:
	window.load('../result/state_svg.svg');

	sys.exit(app.exec_())