

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from PySide2 import QtSvg,QtCore,QtGui,Qt,QtWidgets
import sys, signal, os
from argparse import ArgumentParser
from random import uniform
import time
import pandas as pd
import numpy as np
s=1.0/1.0e10

def m(i):
    return float(i)*s+uniform(-1,1)


DEFAULT_CSS = """
QSlider * {
    border: 0px;
    padding: 0px;
}
QSlider #Head {
    background: #222;
}
QSlider #Span {
    background: #393;
}
QSlider #Span:active {
    background: #282;
}
QSlider #Tail {
    background: #222;
}
QSlider > QSplitter::handle {
    background: #393;
}
QSlider > QSplitter::handle:vertical {
    height: 4px;
}
QSlider > QSplitter::handle:pressed {
    background: #ca5;
}

"""


class SvgWidget(QtSvg.QSvgWidget):
    location_changed = QtCore.Signal(QtCore.QPointF)

    def updateViewBox(self, size):
        w = self.scale * size.width()
        h = self.scale * size.height()
        r = QtCore.QRectF(self.center_x - w/2, self.center_y - h/2,
                         w, h)
        self.renderer().setViewBox(r)

    def center(self):
        self.scale=max(float(self.defViewBox.width())/self.width(),
                       float(self.defViewBox.height())/self.height())
        self.center_x = self.defViewBox.center().x()
        self.center_y = self.defViewBox.center() .y()
        self.updateViewBox(self.size())
        self.repaint()

    def reload(self, path=None):
        QtSvg.QSvgWidget.load(self, self.path)
        self.defViewBox = self.renderer().viewBoxF()
        self.updateViewBox(self.size())

    def resizeEvent(self, evt):
        self.updateViewBox( evt.size())
        QtSvg.QSvgWidget.resizeEvent(self, evt)

    def __init__(self, path):
        QtSvg.QSvgWidget.__init__(self)
        self.path = path
        self.watch = QtCore.QFileSystemWatcher(self)
        self.watch.addPath(self.path)
        self.watch.fileChanged.connect(self.reload)

        self.setMouseTracking(True)
        self.ds = None
        self.scale = 0
        self.center_x = 0
        self.center_y = 0
        self.setPalette( QtGui.QPalette( QtCore.Qt.white ) );
        self.setAutoFillBackground(True)
        QtSvg.QSvgWidget.load(self, path)
        self.defViewBox = self.renderer().viewBoxF()
        self.center()
        #self.setAcceptsHoverEvents(True)

    def updateLocation(self, pos):
        self.location_changed.emit(QtCore.QPointF(
                (pos.x() - self.width()/2)*self.scale + self.center_x,
                (pos.y() - self.height()/2)*self.scale + self.center_y))

    def wheelEvent(self, evt):
        dx = evt.pos().x() - self.width()/2
        dy = evt.pos().y() - self.height()/2
        center_x = self.center_x + dx*self.scale
        center_y = self.center_y + dy*self.scale
        self.scale = self.scale * 1.0025**(evt.angleDelta().y());
        self.center_x = center_x - dx*self.scale
        self.center_y = center_y - dy*self.scale


        self.updateViewBox(self.size())
        self.updateLocation(evt.pos())
        self.repaint()

    def mousePressEvent(self, evt):
        self.ds = evt.localPos()
        self.start_center_x = self.center_x
        self.start_center_y = self.center_y

    def mouseMoveEvent(self, evt):
        self.updateLocation(evt.localPos())
        if not self.ds: return
        dx = evt.localPos().x() - self.ds.x()
        dy = evt.localPos().y() - self.ds.y()
        self.center_x = self.start_center_x - dx*self.scale
        self.center_y = self.start_center_y - dy*self.scale
        self.updateViewBox(self.size())
        self.repaint()

    def mouseReleaseEvent(self, evt):
        self.mouseMoveEvent(evt)
        self.ds = None

def tr(s):
    return QtWidgets.QApplication.translate("SvgViewer", s, None, QtWidgets.QApplication.UnicodeUTF8)

class Visualization(QtWidgets.QMainWindow):
    closed = QtCore.Signal()
    def showLocation(self, point):
        self.statusbar.showMessage("%f %f"%(point.x(), point.y()))

    def load(self, path):
        view = SvgWidget(path)
        #view.location_changed.connect(self.showLocation)
        self.tabs.setCurrentIndex( self.tabs.addTab(view, os.path.basename("%s"%path)))

    def closeTab(self):
        if not self.tabs.currentWidget(): return
        self.tabs.removeTab(self.tabs.currentIndex())

    def center(self):
        if not self.tabs.currentWidget(): return
        self.tabs.currentWidget().center()

    def reload(self):
        if not self.tabs.currentWidget(): return
        self.tabs.currentWidget().reload()

    def nextTab(self):
        if not self.tabs.currentWidget(): return
        self.tabs.setCurrentIndex( (self.tabs.currentIndex() + 1)%self.tabs.count());

    def prevTab(self):
        if not self.tabs.currentWidget(): return
        self.tabs.setCurrentIndex( (self.tabs.currentIndex() - 1)%self.tabs.count());

    def open(self):
        path = QtGui.QFileDialog.getOpenFileName(
            self, "Open File", filter=tr("Svg documents (*.svg);;Any files (*.*)"))
        if path: self.load(path)

    def closeEvent(self, event):
        self.closed.emit()
        event.accept()


    def __init__(self, parent=None):
        print("Created Visualization")
        QtWidgets.QMainWindow.__init__(self, parent)

        self.tabs = QtWidgets.QTabWidget(self)
        self.tabs.setMovable(True)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.closeTab)

        self.statusbar = QtWidgets.QStatusBar(self)
        self.setStatusBar(self.statusbar)

        self.setCentralWidget(self.tabs)

        self.resize(1600, 600)

        self.menubar = QtWidgets.QMenuBar(self)
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuEdit = QtWidgets.QMenu(self.menubar)
        self.setMenuBar(self.menubar)

        self.actionOpen = QtWidgets.QAction(self)
        self.actionOpen.setShortcuts(QtGui.QKeySequence.Open);
        self.actionQuit = QtWidgets.QAction(self)
        self.actionQuit.setShortcuts(QtGui.QKeySequence.Quit);
        self.actionClose = QtWidgets.QAction(self)
        self.actionClose.setShortcuts(QtGui.QKeySequence.Close)
        self.actionCenter = QtWidgets.QAction(self)
        self.actionReload = QtWidgets.QAction(self)

        self.actionNext = QtWidgets.QAction(self)
        self.actionPrev = QtWidgets.QAction(self)

        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionClose)
        self.menuFile.addAction(self.actionQuit)
        self.menuEdit.addAction(self.actionCenter)
        self.menuEdit.addAction(self.actionReload)
        self.menuEdit.addAction(self.actionNext)
        self.menuEdit.addAction(self.actionPrev)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuEdit.menuAction())

        self.actionCenter.triggered.connect(self.center)
        self.actionReload.triggered.connect(self.reload)
        self.actionNext.triggered.connect(self.nextTab)
        self.actionPrev.triggered.connect(self.prevTab)
        self.actionQuit.triggered.connect(self.close)
        self.actionOpen.triggered.connect(self.open)
        self.actionClose.triggered.connect(self.closeTab)

        self.setWindowTitle("Svg Viewer")
        self.menuFile.setTitle("&File")
        self.menuEdit.setTitle("&Edit")
        self.actionOpen.setText("&Open")
        self.actionClose.setText("&Close Tab")
        self.actionQuit.setText("&Quit")
        self.actionCenter.setText("&Center")
        self.actionReload.setText("&Reload")
        self.actionNext.setText("&Next Tab")
        self.actionPrev.setText("&Prev Tab")
        #self.show()
        #self.load('../result/svg/{}.svg'.format(svg))

def handleIntSignal(signum, frame):
    QtGui.qApp.closeAllWindows()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    #parser = ArgumentParser(description="Display SVG files.")
    #parser.add_argument("-v", "--version", help="show version information", default=False, action='store_const', const=True);
    #parser.add_argument("documents", nargs='*')


#opt_parser.add_option("-q", dest="quickly", action="store_true",
#    help="Do it quickly (default=False)")
#(options, args) = opt_

    #parser.parse_args(map(str, app.arguments()))
    """
    if  '-h' in app.arguments()[1:] or '--help' in app.arguments()[1:]:
        print "Usage: svg_view.py <path_to_svg_file>?"
        exit
    """
    window = Visualization()
    window.show()

    #for path in app.arguments()[1:]:
    window.load('../result/state_svg.svg');

    #This is a hack to let the interperter run once every 1/2 second to catch sigint
    timer = QtCore.QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)
    signal.signal(signal.SIGINT, handleIntSignal)

    sys.exit(app.exec_())
