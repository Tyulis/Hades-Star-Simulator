#!§usr/bin/python3
# -*- coding:utf-8 -*-

import sys
from PyQt5.QtWidgets import QApplication
from optimhades.window import MainWindow


if __name__ == "__main__":
	app = QApplication(sys.argv)
	window = MainWindow()
	window.show()
	window.showMaximized()
	app.exec_()
