import sys
import os
import signal
import pandas as pd
p = Path(__file__).resolve().parents[2]
sys.path.append(os.path.abspath(str(p)))
from PyProM.src.data.Eventlog import Eventlog
from PyProM.src.data.xes_reader import XesReader

from PyProM.src.mining.transition_matrix import TransitionMatrix
from PyProM.src.mining.dependency_graph import DependencyGraph
from PyProM.src.mining.heuristic_miner import HeuristicMiner

from PyProM.src.model.fsm import FSM_Miner

from PyProM.src.visualization.svg_widget import Visualization

from PyQt5 import QtSvg,QtCore,QtGui,Qt,QtWidgets
import multiprocessing



if __name__ == '__main__':
	eventlog = Eventlog.from_txt('/Users/GYUNAM/Documents/example/repairExample.txt')
	eventlog = eventlog.assign_caseid('Case ID')
	eventlog = eventlog.assign_activity('Activity')
	eventlog = eventlog.assign_resource('Resource')
	eventlog = eventlog.assign_timestamp('Complete Timestamp')
	eventlog = eventlog.clear_columns()

	#HM

	HM = HeuristicMiner(eventlog = eventlog)

	fsm = FSM_Miner()
	fsm_graph = fsm._create_graph(HM.dependency_relation)
	fsm.get_graph_info(fsm_graph)
	dot = fsm.get_dot(fsm_graph)

	app = QtWidgets.QApplication(sys.argv)


	window = Visualization()
	window.show()

	#for path in app.arguments()[1:]:
	window.load('../result/state_svg.svg');

	sys.exit(app.exec_())