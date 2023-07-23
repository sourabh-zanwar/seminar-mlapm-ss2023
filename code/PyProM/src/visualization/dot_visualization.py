from svg_widget import Visualization
from PyQt5 import QtSvg,QtCore,QtGui,Qt,QtWidgets
import sys

class DotVisualization(Visualization):
	"""docstring for DotVisualization"""
	def __init__(self, parent = None):
		super(DotVisualization, self).__init__(parent)
		app = QtWidgets.QApplication(sys.argv)
		Visualization.__init__(self)