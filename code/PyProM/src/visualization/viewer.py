from svg_widget import Visualization

app = QtWidgets.QApplication(sys.argv)


	window = Visualization()
	window.show()

	#for path in app.arguments()[1:]:
	window.load('/Users/GYUNAM/Desktop/state_svg.svg');

	sys.exit(app.exec_())
