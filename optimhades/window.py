# -*- coding:utf-8 -*-

import os
import heapq
import itertools
from math import *
from .elements import *
from .system import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

SCENE_SIZE = 1750
SCENE_CENTER = SCENE_SIZE // 2
HEXAGON_WIDTH = 250
HEXAGON_RADIUS = HEXAGON_WIDTH // 2
HEXAGON_LRADIUS = HEXAGON_RADIUS * (sqrt(3) / 2)
AU_SIZE = HEXAGON_LRADIUS * 2 / 700
HUB_RADIUS = 10
HUB_BODY_COLOR = QColor(20, 10, 100)
HUB_OUTLINE_COLOR = QColor(20, 100, 255)
STAR_RADIUS = HEXAGON_RADIUS // 2

PLANET_RADIUS = {
	1: HEXAGON_RADIUS // 6,
	2: HEXAGON_RADIUS // 5,
	3: HEXAGON_RADIUS // 4,
	4: HEXAGON_RADIUS // 3,
}

PLANET_COLORS = {
	"Desert": QColor(210, 160, 60),
	"Lava": QColor(255, 50, 0),
	"Water": QColor(0, 128, 255),
	"Terran": QColor(0, 180, 60),
	"Gas": QColor(130, 0, 255),
	"Ice": QColor(0, 240, 255),
	"Star": QColor(255, 255, 0),
	"Station": QColor(255, 255, 255),
}

class SystemBox (QGraphicsView):
	toolResult = pyqtSignal()
	distanceChanged = pyqtSignal()

	def __init__(self, system):
		super().__init__()
		self.scene = QGraphicsScene(QRectF(0, 0, SCENE_SIZE, SCENE_SIZE))
		self.setScene(self.scene)
		self.updateSystem(system)
		self.scene.setBackgroundBrush(QBrush(QColor(20, 20, 40)))
		self.tool = "select"
		self.pathstart = self.pathend = 0
		self.pathlastset = 0
		self.distratio = 0
		self.planetframe = None

	def updateSystem(self, system):
		self.system = system
		if system is not None:
			self.renderSystem()

	def renderSystem(self):
		self.clearScene()
		if self.system is not None:
			self.drawGrid()
			self.drawStar()
			for planet in self.system.planets:
				self.drawPlanet(planet)
			for hub in self.system.hubs:
				self.drawHub(hub)
			self.drawPath()

	def drawPath(self):
		if self.pathstart == self.pathend:
			return
		bestlength, bestpath = self.bestPath(self.pathstart, self.pathend)
		pathpen = QPen(QColor(255, 128, 50, 150))
		pathpen.setWidth(6)
		pathpen.setStyle(Qt.DashLine)
		last = "start"
		for point in bestpath[1:-1]:
			if last == "start":
				startpos = self.system.planets[self.pathstart].position
			else:
				startpos = self.system.hubs[last].link.position
			if point == "end":
				endpos = self.system.planets[self.pathend].position
			else:
				endpos = self.system.hubs[point].position
			self.scene.addLine(startpos[0], startpos[1], endpos[0], endpos[1], pathpen)
			last = point

	def bestPath(self, start, end):
		graph = self.generateGraph(start, end)
		heap = []
		for neighbor in graph["start"]:
			heapq.heappush(heap, (graph["start"][neighbor], ["start", neighbor]))
		visited = set()
		visited.add("start")
		while heap:
			length, path = heapq.heappop(heap)
			dest = path[-1]
			if dest in visited:
				continue
			if dest == "end":
				return length, path + ["end"]
			for neighbor in graph[dest]:
				if neighbor not in visited:
					newlength = length + graph[dest][neighbor]
					newpath = path + [neighbor]
					heapq.heappush(heap, (newlength, newpath))
		return None

	def generateGraph(self, start, end):
		startplanet = self.system.planets[start]
		endplanet = self.system.planets[end]
		maxdist = self.distance(startplanet, endplanet)
		graph = {i: {} for i in range(len(self.system.hubs))}
		graph["start"] = {"end": maxdist}
		graph["end"] = {"start": maxdist}
		for i, hub in enumerate(self.system.hubs):
			link = self.system.hubs.index(hub.link)
			if i not in graph["start"] and link not in graph["start"] and i not in graph["end"] and link not in graph["end"]:
				hubdist = self.distance(startplanet, hub)
				linkdist = self.distance(startplanet, hub.link)
				if hubdist <= linkdist:
					graph["start"][i] = hubdist
					graph[i]["start"] = hubdist
				else:
					graph["start"][link] = linkdist
					graph[link]["start"] = linkdist
				hubdist = self.distance(endplanet, hub)
				linkdist = self.distance(endplanet, hub.link)
				if hubdist <= linkdist:
					graph["end"][link] = hubdist
					graph[link]["end"] = hubdist
				else:
					graph["end"][i] = linkdist
					graph[i]["end"] = linkdist
			for j, sechub in enumerate(self.system.hubs):
				seclink = self.system.hubs.index(sechub.link)
				if j not in graph[i] and seclink not in graph[i] and j != i and seclink != i:
					hubdist = self.distance(hub.link, sechub)
					linkdist = self.distance(hub.link, sechub.link)
					if hubdist <= linkdist:
						graph[i][j] = hubdist
					else:
						graph[i][seclink] = linkdist
		return graph

	def distance(self, a, b):
		return QLineF(a.position[0], a.position[1], b.position[0], b.position[1]).length()

	def computePathDistance(self):
		if self.pathstart == self.pathend:
			return 0
		bestlength, bestpath = self.bestPath(self.pathstart, self.pathend)
		return bestlength

	def computeDistanceRatio(self):
		if len(self.system.planets) <= 0:
			return 0
		result = 0
		total = 0
		totaldist = 0
		for i, planet1 in enumerate(self.system.planets):
			for j, planet2 in enumerate(self.system.planets):
				if i == j:
					continue
				maxdist = self.distance(planet1, planet2)
				dist, path = self.bestPath(i, j)
				income = planet1.cargoPerHour() + planet2.cargoPerHour()
				result += income * (maxdist - dist)
				total += income
				totaldist += maxdist
		return result / (total * totaldist) * 10000

	def drawPlanet(self, planet):
		radius = PLANET_RADIUS[planet.tier]
		item = self.scene.addEllipse(planet.position[0] - radius, planet.position[1] - radius, radius * 2, radius * 2)
		item.setPen(QPen(PLANET_COLORS[planet.type]))
		item.setBrush(QBrush(PLANET_COLORS[planet.type]))

	def drawStar(self):
		item = self.scene.addEllipse(SCENE_CENTER - STAR_RADIUS, SCENE_CENTER - STAR_RADIUS, STAR_RADIUS * 2, STAR_RADIUS * 2)
		item.setPen(QPen(PLANET_COLORS["Star"]))
		item.setBrush(QBrush(PLANET_COLORS["Star"]))

	def drawHub(self, hub):
		item = self.scene.addEllipse(hub.position[0] - HUB_RADIUS, hub.position[1] - HUB_RADIUS, HUB_RADIUS * 2, HUB_RADIUS * 2)
		outpen = QPen(HUB_OUTLINE_COLOR)
		outpen.setWidth(6)
		item.setPen(outpen)
		item.setBrush(QBrush(HUB_BODY_COLOR))
		linepen = QPen(QColor(255, 255, 255, 180))
		linepen.setWidth(4)
		if hub.link is not None:
			line = self.scene.addLine(hub.position[0], hub.position[1], hub.link.position[0], hub.link.position[1], linepen)

	def drawGrid(self):
		self.sectors = {}
		for level in range(0, 4):
			radius = (sqrt(3) / 2) * HEXAGON_RADIUS * level
			number = 6 * level
			if level == 0:  # Star
				polygon = QPolygonF((
					QPointF(SCENE_CENTER - HEXAGON_RADIUS, SCENE_CENTER),
					QPointF(SCENE_CENTER - HEXAGON_RADIUS // 2, SCENE_CENTER - HEXAGON_LRADIUS),
					QPointF(SCENE_CENTER + HEXAGON_RADIUS // 2, SCENE_CENTER - HEXAGON_LRADIUS),
					QPointF(SCENE_CENTER + HEXAGON_RADIUS, SCENE_CENTER),
					QPointF(SCENE_CENTER + HEXAGON_RADIUS // 2, SCENE_CENTER + HEXAGON_LRADIUS),
					QPointF(SCENE_CENTER - HEXAGON_RADIUS // 2, SCENE_CENTER + HEXAGON_LRADIUS),
				))
				self.sectors["D4"] = polygon
				item = self.scene.addPolygon(polygon)
				item.setBrush(QBrush(QColor(0, 0, 0, 0)))
				item.setPen(QPen(QColor(255, 255, 255, 150)))
			else:
				centerradius = (level * 2) * HEXAGON_LRADIUS
				for i in range(6):
					angle = radians(60 * i + 30)
					centerx = cos(angle) * centerradius + SCENE_CENTER
					centery = sin(angle) * centerradius + SCENE_CENTER
					polygon = QPolygonF((
						QPointF(centerx - HEXAGON_RADIUS, centery),
						QPointF(centerx - HEXAGON_RADIUS // 2, centery - HEXAGON_LRADIUS),
						QPointF(centerx + HEXAGON_RADIUS // 2, centery - HEXAGON_LRADIUS),
						QPointF(centerx + HEXAGON_RADIUS, centery),
						QPointF(centerx + HEXAGON_RADIUS // 2, centery + HEXAGON_LRADIUS),
						QPointF(centerx - HEXAGON_RADIUS // 2, centery + HEXAGON_LRADIUS),
					))
					sector = {
						1: ("E3", "D3", "C3", "C4", "D5", "E4"),
						2: ("F2", "D2", "B2", "B4", "D6", "F4"),
						3: ("G1", "D1", "A1", "A4", "D7", "G4"),
					}[level][i]
					self.sectors[sector] = polygon
					item = self.scene.addPolygon(polygon)
					item.setBrush(QBrush(QColor(0, 0, 0, 0)))
					item.setPen(QPen(QColor(255, 255, 255, 150)))
				if level == 2:
					centerradius = (level + 1) * HEXAGON_RADIUS
					for i in range(6):
						angle = radians(60 * i)
						centerx = cos(angle) * centerradius + SCENE_CENTER
						centery = sin(angle) * centerradius + SCENE_CENTER
						polygon = QPolygonF((
							QPointF(centerx - HEXAGON_RADIUS, centery),
							QPointF(centerx - HEXAGON_RADIUS // 2, centery - HEXAGON_LRADIUS),
							QPointF(centerx + HEXAGON_RADIUS // 2, centery - HEXAGON_LRADIUS),
							QPointF(centerx + HEXAGON_RADIUS, centery),
							QPointF(centerx + HEXAGON_RADIUS // 2, centery + HEXAGON_LRADIUS),
							QPointF(centerx - HEXAGON_RADIUS // 2, centery + HEXAGON_LRADIUS),
						))
						sector = ("F3", "E2", "C2", "B3", "C5", "E5")[i]
						self.sectors[sector] = polygon
						item = self.scene.addPolygon(polygon)
						item.setBrush(QBrush(QColor(0, 0, 0, 0)))
						item.setPen(QPen(QColor(255, 255, 255, 150)))
				elif level == 3:
					centerradius = sqrt(((level * 1.5) * HEXAGON_RADIUS) ** 2 + HEXAGON_LRADIUS ** 2)
					for i in range(6):
						angle = radians(60 * i + 32 / 3)
						centerx = cos(angle) * centerradius + SCENE_CENTER
						centery = sin(angle) * centerradius + SCENE_CENTER
						polygon = QPolygonF((
							QPointF(centerx - HEXAGON_RADIUS, centery),
							QPointF(centerx - HEXAGON_RADIUS // 2, centery - HEXAGON_LRADIUS),
							QPointF(centerx + HEXAGON_RADIUS // 2, centery - HEXAGON_LRADIUS),
							QPointF(centerx + HEXAGON_RADIUS, centery),
							QPointF(centerx + HEXAGON_RADIUS // 2, centery + HEXAGON_LRADIUS),
							QPointF(centerx - HEXAGON_RADIUS // 2, centery + HEXAGON_LRADIUS),
						))
						sector = ("G2", "E1", "B1", "A3", "C6", "F5")[i]
						self.sectors[sector] = polygon
						item = self.scene.addPolygon(polygon)
						item.setBrush(QBrush(QColor(0, 0, 0, 0)))
						item.setPen(QPen(QColor(255, 255, 255, 150)))
					for i in range(6):
						angle = radians(60 * i - 32 / 3)
						centerx = cos(angle) * centerradius + SCENE_CENTER
						centery = sin(angle) * centerradius + SCENE_CENTER
						polygon = QPolygonF((
							QPointF(centerx - HEXAGON_RADIUS, centery),
							QPointF(centerx - HEXAGON_RADIUS // 2, centery - HEXAGON_LRADIUS),
							QPointF(centerx + HEXAGON_RADIUS // 2, centery - HEXAGON_LRADIUS),
							QPointF(centerx + HEXAGON_RADIUS, centery),
							QPointF(centerx + HEXAGON_RADIUS // 2, centery + HEXAGON_LRADIUS),
							QPointF(centerx - HEXAGON_RADIUS // 2, centery + HEXAGON_LRADIUS),
						))
						sector = ("G3", "F1", "C1", "A2", "B5", "E6")[i]
						self.sectors[sector] = polygon
						item = self.scene.addPolygon(polygon)
						item.setBrush(QBrush(QColor(0, 0, 0, 0)))
						item.setPen(QPen(QColor(255, 255, 255, 150)))

	def drawFrame(self, planet):
		if self.planetframe is not None:
			self.scene.removeItem(self.planetframe)
		self.planetframe = self.scene.addRect(self.planetRect(planet), QPen(QColor(255, 128, 0)))

	def clearScene(self):
		for item in self.scene.items():
			self.scene.removeItem(item)

	def changeTool(self, tool):
		self.tool = tool
		self.pathstart = self.pathend = 0

	def mousePressEvent(self, event):
		coords = self.mapToScene(event.pos())
		if self.tool == "select":
			for i in range(len(self.system.planets)):
				if self.planetRect(self.system.planets[i]).contains(coords):
					self.drawFrame(self.system.planets[i])
					self.result = i
					self.toolResult.emit()
					return
		elif self.tool == "add":
			self.result = [coords.x(), coords.y()]
			self.toolResult.emit()
		elif self.tool == "move":
			self.basepos = coords
			for i in range(len(self.system.planets)):
				if self.planetRect(self.system.planets[i]).contains(coords):
					self.movingobject = ["P", i]
					return
			for i in range(len(self.system.hubs)):
				if self.hubRect(self.system.hubs[i]).contains(coords):
					self.movingobject = ["H", i]
					return
			self.movingobject = None
		elif self.tool == "addlane":
			self.result = [coords.x(), coords.y()]
			self.toolResult.emit()
		elif self.tool == "del":
			for i in range(len(self.system.planets)):
				if self.planetRect(self.system.planets[i]).contains(coords):
					if QMessageBox.question(self, "Confirm removal", "Do you really want to remove this planet ?", QMessageBox.Yes | QMessageBox.Cancel, QMessageBox.Cancel) == QMessageBox.Yes:
						del self.system.planets[i]
			for i in range(len(self.system.hubs)):
				if self.hubRect(self.system.hubs[i]).contains(coords):
					if QMessageBox.question(self, "Confirm removal", "Do you really want to remove this warp lane ?", QMessageBox.Yes | QMessageBox.Cancel, QMessageBox.Cancel) == QMessageBox.Yes:
						toremove = self.system.hubs[i]
						self.system.hubs.remove(self.system.hubs[i].link)
						self.system.hubs.remove(toremove)
						break
			self.pathlength = self.computePathDistance()
			self.distratio = self.computeDistanceRatio()
			self.distanceChanged.emit()
			self.renderSystem()
		elif self.tool == "hydro":
			index = None
			for i in range(len(self.system.planets)):
				if self.planetRect(self.system.planets[i]).contains(coords):
					index = i
			if index is not None:
				if self.pathlastset == 0:
					self.pathstart = self.pathend = index
					self.pathlastset = 1
				else:
					self.pathend = index
					self.pathlastset = 0
					self.pathlength = self.computePathDistance()
					self.distanceChanged.emit()
			self.renderSystem()

	def mouseMoveEvent(self, event):
		coords = self.mapToScene(event.pos())
		if self.tool == "move":
			if self.movingobject is None:
				return
			diff = coords - self.basepos
			if self.movingobject[0] == "H":
				self.system.hubs[self.movingobject[1]].position[0] += diff.x()
				self.system.hubs[self.movingobject[1]].position[1] += diff.y()
			elif self.movingobject[0] == "P":
				self.system.planets[self.movingobject[1]].position[0] += diff.x()
				self.system.planets[self.movingobject[1]].position[1] += diff.y()
			self.basepos = coords
			self.pathlength = self.computePathDistance()
			self.distratio = self.computeDistanceRatio()
			self.distanceChanged.emit()
			self.renderSystem()

	def mouseReleaseEvent(self, event):
		coords = self.mapToScene(event.pos())
		if self.tool == "move":
			if self.movingobject is None:
				return
			diff = coords - self.basepos
			if self.movingobject[0] == "H":
				self.system.hubs[self.movingobject[1]].position[0] += diff.x()
				self.system.hubs[self.movingobject[1]].position[1] += diff.y()
			elif self.movingobject[0] == "P":
				self.system.planets[self.movingobject[1]].position[0] += diff.x()
				self.system.planets[self.movingobject[1]].position[1] += diff.y()
			self.pathlength = self.computePathDistance()
			self.distratio = self.computeDistanceRatio()
			self.distanceChanged.emit()
			self.renderSystem()
			self.result = self.movingobject
			self.toolResult.emit()

	def planetRect(self, planet):
		radius = PLANET_RADIUS[planet.tier]
		return QRectF(planet.position[0] - radius, planet.position[1] - radius, radius * 2, radius * 2)

	def hubRect(self, hub):
		return QRectF(hub.position[0] - HUB_RADIUS, hub.position[1] - HUB_RADIUS, HUB_RADIUS * 2, HUB_RADIUS * 2)

	def updateGraphics(self):
		self.renderSystem()

class ActionBox (QWidget):
	def __init__(self, system):
		super().__init__()
		self.system = system
		self.tool = "select"
		self.lastitem = None
		self.hydroresult = 0
		self.distratio = 0
		self.buildUI()

	def buildUI(self):
		self.layout = QVBoxLayout()
		self.selectbutton = QPushButton("Planets' infos")
		self.selectbutton.setCheckable(True)
		self.selectbutton.setChecked(True)
		self.selectbutton.clicked.connect(self.selectChecked)
		self.layout.addWidget(self.selectbutton)
		self.addbutton = QPushButton("Add planets")
		self.addbutton.setCheckable(True)
		self.addbutton.clicked.connect(self.addPlanetChecked)
		self.layout.addWidget(self.addbutton)
		self.addlanebtn = QPushButton("Add warp lanes")
		self.addlanebtn.setCheckable(True)
		self.addlanebtn.clicked.connect(self.addLaneChecked)
		self.layout.addWidget(self.addlanebtn)
		self.movebutton = QPushButton("Move things")
		self.movebutton.setCheckable(True)
		self.movebutton.clicked.connect(self.moveChecked)
		self.layout.addWidget(self.movebutton)
		self.delbutton = QPushButton("Remove things")
		self.delbutton.setCheckable(True)
		self.delbutton.clicked.connect(self.removePlanetChecked)
		self.layout.addWidget(self.delbutton)
		self.hydrobutton = QPushButton("Compute hydrogen consumption")
		self.hydrobutton.setCheckable(True)
		self.hydrobutton.clicked.connect(self.computeHydrogenChecked)
		self.layout.addWidget(self.hydrobutton)
		self.optibutton = QPushButton("Optimize warp lanes")
		self.optibutton.setCheckable(True)
		self.optibutton.clicked.connect(self.optimisationChecked)
		self.layout.addWidget(self.optibutton)
		self.infobutton = QPushButton("System informations")
		self.infobutton.setCheckable(True)
		self.infobutton.clicked.connect(self.systemInfoChecked)
		self.layout.addWidget(self.infobutton)
		self.layout.addItem(QSpacerItem(0, self.height()))
		self.setLayout(self.layout)

		self.hydrosettings = QWidget()
		self.hydrolyt = QGridLayout()
		self.hydrolyt.addWidget(QLabel("Hydrogen / 100AU : "), 0, 0)
		self.hydrolyt.addWidget(QLabel("Distance (AU) : "), 1, 0)
		self.hydrolyt.addWidget(QLabel("Hydrogen consumed : "), 2, 0)
		self.hydroconso = QDoubleSpinBox()
		self.hydroconso.setDecimals(1)
		self.hydroconso.setSingleStep(0.1)
		self.hydroconso.setMinimum(0)
		self.hydroconso.valueChanged.connect(self.hydroConsoChanged)
		self.hydrolyt.addWidget(self.hydroconso, 0, 1)
		self.distlabel = QLabel(str(round(self.hydroresult, 2)))
		self.hydrolyt.addWidget(self.distlabel, 1, 1)
		self.resultlabel = QLabel(str(round(self.hydroresult * self.hydroconso.value() / 100, 2)))
		self.hydrolyt.addWidget(self.resultlabel, 2, 1)
		self.hydrosettings.setLayout(self.hydrolyt)

		self.optisettings = QWidget()
		self.optilyt = QGridLayout()
		self.optilyt.addWidget(QLabel("Optimisation indicator : "), 0, 0)
		self.optilyt.addWidget(QLabel("<i>This indicator should be as high as possible</i>"), 1, 0)
		self.distratiolbl = QLabel(str(round(self.distratio, 3)) + " %")
		self.optilyt.addWidget(self.distratiolbl, 0, 1)
		self.optisettings.setLayout(self.optilyt)

	def uncheckAll(self, checked):
		for i in range(self.layout.count()):
			widget = self.layout.itemAt(i).widget()
			if widget != checked and widget is not None:
				if type(widget) == QPushButton:
					widget.setChecked(False)

	def selectChecked(self):
		self.uncheckAll(self.selectbutton)
		self.tool = "select"
		self.changeTool.emit()

	def addPlanetChecked(self):
		self.uncheckAll(self.addbutton)
		self.tool = "add"
		self.changeTool.emit()

	def removePlanetChecked(self):
		self.uncheckAll(self.delbutton)
		self.tool = "del"
		self.changeTool.emit()

	def moveChecked(self):
		self.uncheckAll(self.movebutton)
		self.tool = "move"
		self.changeTool.emit()

	def addLaneChecked(self):
		self.uncheckAll(self.addlanebtn)
		self.tool = "addlane"
		self.changeTool.emit()

	def computeHydrogenChecked(self):
		self.uncheckAll(self.hydrobutton)
		self.tool = "hydro"
		if self.lastitem is not None:
			self.layout.removeWidget(self.lastitem)
		self.layout.addWidget(self.hydrosettings)
		self.lastitem = self.hydrosettings
		self.changeTool.emit()

	def optimisationChecked(self):
		self.uncheckAll(self.optibutton)
		self.tool = "opti"
		if self.lastitem is not None:
			self.layout.removeWidget(self.lastitem)
		self.layout.addWidget(self.optisettings)
		self.lastitem = self.optisettings
		self.changeTool.emit()

	def systemInfoChecked(self):
		self.uncheckAll(self.infobutton)
		self.tool = "info"
		self.changeTool.emit()

	def hydroConsoChanged(self, value):
		self.resultlabel.setText(str(round(self.hydroresult * self.hydroconso.value() / 100, 1)))

	def setToolResult(self, result):
		pass

	def setDistance(self, result):
		self.hydroresult = result
		self.distlabel.setText(str(round(self.hydroresult, 2)))
		self.resultlabel.setText(str(round(self.hydroresult * self.hydroconso.value() / 100, 1)))

	def setDistanceRatio(self, ratio):
		self.distratio = ratio
		self.distratiolbl.setText(str(round(self.distratio, 3)) + " %")

	def updateData(self):
		pass

	changeTool = pyqtSignal()

class MainWindow (QMainWindow):
	def __init__(self):
		super().__init__()
		self.system = None
		self.tool = "select"
		self.buildUI()
		self.setWindowTitle("Hades Star optimizer")

	def buildUI(self):
		self.systembox = SystemBox(self.system)
		self.systembox.toolResult.connect(self.toolResult)
		self.systembox.distanceChanged.connect(self.changeDistance)
		self.actionbox = ActionBox(self.system)
		self.actionbox.changeTool.connect(self.changeTool)
		self.setCentralWidget(self.systembox)
		self.actiondock = QDockWidget("Actions")
		self.actiondock.setWidget(self.actionbox)
		self.addDockWidget(Qt.RightDockWidgetArea, self.actiondock)

		self.menubar = self.menuBar()
		self.filemenu = self.menubar.addMenu("File")
		newact = self.filemenu.addAction("New system")
		newact.setShortcut("Ctrl+N")
		newact.triggered.connect(self.newSystem)
		openact = self.filemenu.addAction("Open system")
		openact.setShortcut("Ctrl+O")
		openact.triggered.connect(self.openSystem)
		saveact = self.filemenu.addAction("Save system")
		saveact.setShortcut("Ctrl+S")
		saveact.triggered.connect(self.saveSystem)
		closeact = self.filemenu.addAction("Close")
		closeact.setShortcut("Ctrl+Q")
		closeact.triggered.connect(self.closeApp)

	def newSystem(self):
		self.system = System()
		self.systembox.updateSystem(self.system)

	def openSystem(self):
		filename = QFileDialog.getOpenFileName(self, "Open system", ".", "JSON packed system (*.json)")
		if filename[0]:
			self.system = System.load(filename[0])
			self.systembox.updateSystem(self.system)

	def saveSystem(self):
		if self.system.filename is None:
			self.system.filename = QFileDialog.getSaveFileName(self, "Save system", ".", "JSON packed system (*.json)")[0]
		self.system.save()

	def closeApp(self):
		if self.system != None:
			if QMessageBox.question(self, "Quitting app", "Save the system ?", QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
				self.saveSystem()
		self.close()
		qApp.quit()

	def changeTool(self):
		self.tool = self.actionbox.tool
		self.systembox.changeTool(self.actionbox.tool)
		if self.tool == "addlane":
			self.hubnum = 0
		elif self.tool == "opti":
			self.actionbox.setDistanceRatio(self.systembox.computeDistanceRatio())
		elif self.tool == "info":
			SystemInfoDialog.run(self.system, self.systembox.computeDistanceRatio())

	def toolResult(self):
		result = self.systembox.result
		if self.tool == "select":
			planet = PlanetDialog.run(self.system.planets[result])
			if planet is not None:
				self.system.planets[result] = planet
		elif self.tool == "add":
			planet = PlanetDialog.run(makePlanet("Desert", 1, 1, self.systembox.result))
			if planet is not None:
				self.system.planets.append(planet)
		elif self.tool == "addlane":
			if self.hubnum == 0:
				self.firsthub = WarpLaneHub(result)
				self.system.hubs.append(self.firsthub)
				self.hubnum = 1
			else:
				hub = WarpLaneHub(result, self.firsthub)
				self.firsthub.link = hub
				self.system.hubs.append(hub)
				self.hubnum = 0
				self.systembox.pathlength = self.systembox.computePathDistance()
				self.systembox.distratio = self.systembox.computeDistanceRatio()
				self.changeDistance()
		elif self.tool == "hydro":
			self.actionbox.setDistance(result)
		else:
			self.actionbox.setToolResult(result)
		self.systembox.updateGraphics()

	def changeDistance(self):
		self.actionbox.setDistance(self.systembox.pathlength)
		self.actionbox.setDistanceRatio(self.systembox.distratio)
