# -*- coding: utf-8 -*-
"""
Created on Fri Apr 29 16:52:28 2011

@author: -
"""
# This example is from the PyQt4 tutorial and is slightly modified to
# illustrate how to integrate PyQt4 with Houdini.

from PyQt4 import QtCore
from PyQt4 import QtGui
from pyubic.houdini import hou_pyqt_helper as pyqt_houdini

class FontDialog(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)

        hbox = QtGui.QHBoxLayout()

        self.setGeometry(500, 300, 250, 110)
        self.setWindowTitle('FontDialog')

        button = QtGui.QPushButton('Change Font...', self)
        button.setFocusPolicy(QtCore.Qt.NoFocus)
        button.move(20, 20)

        hbox.addWidget(button)

        self.connect(button, QtCore.SIGNAL('clicked()'), self.showDialog)

        self.label = QtGui.QLabel('This is some Sample Text', self)
        self.label.move(130, 20)

        hbox.addWidget(self.label, 1)
        self.setLayout(hbox)

    def showDialog(self):
        font, ok = QtGui.QFontDialog.getFont()
        if ok:
            self.label.setFont(font)

app = QtGui.QApplication(['houdini'])
dialog = FontDialog()
dialog.show()

# The main difference from a normal PyQt application is that instead of calling
# app.exec_() you call pyqt_houdini.exec_(app, dialog1, ...).
pyqt_houdini.exec_(app, dialog)
