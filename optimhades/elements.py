# -*- coding:utf-8 -*-

from PyQt5.QtWidgets import *
from .system import *


class PlanetDialog (QDialog):
	@classmethod
	def run(cls, planet):
		self = cls()
		self.planet = changePlanetType(planet, planet.type)
		self.layout = QGridLayout()
		self.layout.addWidget(QLabel("Type"), 0, 0)
		self.layout.addWidget(QLabel("Max level"), 1, 0)
		self.layout.addWidget(QLabel("Level"), 2, 0)
		self.layout.addWidget(QLabel("Shipment value per hour"), 3, 0)
		self.layout.addWidget(QLabel("Credits per hour"), 4, 0)
		self.layout.addWidget(QLabel("Hydrogen per hour"), 5, 0)
		self.layout.addWidget(QLabel("Credits storage"), 6, 0)
		self.layout.addWidget(QLabel("Hydrogen storage"), 7, 0)
		self.layout.addWidget(QLabel("Max shipments"), 8, 0)
		self.layout.addWidget(QLabel("Max shipments per hour"), 9, 0)
		self.layout.addWidget(QLabel("Upgrade cost"), 10, 0)
		self.layout.addWidget(QLabel("Upgrade break even"), 11, 0)
		self.typebox = QComboBox()
		self.typebox.addItems(list(PLANET_TYPES.keys()))
		self.typebox.setCurrentText(planet.type)
		self.layout.addWidget(self.typebox, 0, 1)
		self.typebox.currentTextChanged.connect(self.changePlanetType)
		self.tierbox = QComboBox()
		self.tierbox.addItems([str(item) for item in PLANET_TIERS.keys()])
		self.tierbox.setCurrentText(str(PLANET_MAX_LEVELS[planet.tier]))
		self.tierbox.currentTextChanged.connect(self.changePlanetTier)
		self.layout.addWidget(self.tierbox, 1, 1)
		self.levelbox = QSpinBox()
		self.levelbox.setMinimum(1)
		self.levelbox.setMaximum(40)
		self.levelbox.setValue(planet.level)
		self.levelbox.valueChanged.connect(self.changePlanetLevel)
		self.layout.addWidget(self.levelbox, 2, 1)
		self.valueperhour_lbl = QLabel(str(planet.cargoPerHour()))
		self.layout.addWidget(self.valueperhour_lbl, 3, 1)
		self.creditsperhour_lbl = QLabel(str(planet.creditsPerHour()))
		self.layout.addWidget(self.creditsperhour_lbl, 4, 1)
		self.hydroperhour_lbl = QLabel(str(planet.hydrogenPerHour()))
		self.layout.addWidget(self.hydroperhour_lbl, 5, 1)
		self.creditstorage_lbl = QLabel(str(planet.creditStorage()))
		self.layout.addWidget(self.creditstorage_lbl, 6, 1)
		self.hydrostorage_lbl = QLabel(str(planet.hydrogenStorage()))
		self.layout.addWidget(self.hydrostorage_lbl, 7, 1)
		self.maxshipments_lbl = QLabel(str(planet.maxShipments()))
		self.layout.addWidget(self.maxshipments_lbl, 8, 1)
		self.shipmentsperhour_lbl = QLabel(str(planet.shipmentsPerHour()))
		self.layout.addWidget(self.shipmentsperhour_lbl, 9, 1)
		self.upgradecost_lbl = QLabel(str(planet.upgradeCost()))
		self.layout.addWidget(self.upgradecost_lbl, 10, 1)
		self.breakeven_lbl = QLabel(self.formatDuration(planet.upgradeBreakEven()))
		self.layout.addWidget(self.breakeven_lbl, 11, 1)

		self.okbutton = QPushButton("Confirm")
		self.okbutton.clicked.connect(self.confirm)
		self.layout.addWidget(self.okbutton, 12, 0)
		self.cancelbutton = QPushButton("Cancel")
		self.cancelbutton.clicked.connect(self.cancel)
		self.layout.addWidget(self.cancelbutton, 12, 1)
		self.setLayout(self.layout)
		self.exec_()
		if self.result() == QDialog.Accepted:
			return makePlanet(self.typebox.currentText(), PLANET_TIERS[int(self.tierbox.currentText())], self.levelbox.value(), planet.position)
		else:
			return None

	def updateValues(self):
		self.valueperhour_lbl.setText(str(self.planet.cargoPerHour()))
		self.creditsperhour_lbl.setText(str(self.planet.creditsPerHour()))
		self.hydroperhour_lbl.setText(str(self.planet.hydrogenPerHour()))
		self.creditstorage_lbl.setText(str(self.planet.creditStorage()))
		self.hydrostorage_lbl.setText(str(self.planet.hydrogenStorage()))
		self.maxshipments_lbl.setText(str(self.planet.maxShipments()))
		self.shipmentsperhour_lbl.setText(str(self.planet.shipmentsPerHour()))
		self.upgradecost_lbl.setText(str(self.planet.upgradeCost()))
		self.breakeven_lbl.setText(self.formatDuration(self.planet.upgradeBreakEven()))

	def changePlanetLevel(self):
		if self.levelbox.value() > int(self.tierbox.currentText()):
			self.levelbox.setValue(self.planet.level)
			QMessageBox.warning(self, "Error", "The selected level is above the max level")
			return
		self.planet.level = self.levelbox.value()
		self.updateValues()

	def changePlanetTier(self):
		if PLANET_TIERS[int(self.tierbox.currentText())] not in PLANET_TYPE_TIERS[self.typebox.currentText()]:
			self.tierbox.setCurrentText(str(PLANET_MAX_LEVELS[self.planet.tier]))
			QMessageBox.warning(self, "Error", "The selected max level is not compatible with the planet type")
			return
		self.planet.tier = PLANET_TIERS[int(self.tierbox.currentText())]
		self.updateValues()

	def changePlanetType(self):
		self.planet = changePlanetType(self.planet, self.typebox.currentText())
		if PLANET_TIERS[int(self.tierbox.currentText())] not in PLANET_TYPE_TIERS[self.typebox.currentText()]:
			self.planet.tier = min(self.planet.SHIPMENT_STORAGE.keys())
			self.tierbox.setCurrentText(str(PLANET_MAX_LEVELS[self.planet.tier]))
		if self.levelbox.value() > int(self.tierbox.currentText()):
			self.planet.level = PLANET_MAX_LEVELS[self.planet.tier]
			self.levelbox.setValue(self.planet.level)
		self.updateValues()

	def formatDuration(self, seconds):
		days = seconds // day
		hours = (seconds % day) // hour
		minutes = (seconds % hour) // mn
		return "%d d, %d h, %d min, %d s" % (days, hours, minutes, seconds % mn)

	def confirm(self):
		if PLANET_TIERS[int(self.tierbox.currentText())] not in PLANET_TYPE_TIERS[self.typebox.currentText()]:
			QMessageBox.warning(self, "Error", "The selected max level is not compatible with the planet type")
		elif self.levelbox.value() > int(self.tierbox.currentText()):
			QMessageBox.warning(self, "Error", "The selected level is above the max level")
		else:
			self.accept()
		return

	def cancel(self):
		self.reject()


class SystemInfoDialog (QDialog):
	@classmethod
	def run(cls, system, efficiency):
		self = cls()
		self.layout = QGridLayout()
		self.layout.addWidget(QLabel("Shipments generated per hour"), 0, 0)
		self.layout.addWidget(QLabel("Shipments value per hour"), 1, 0)
		self.layout.addWidget(QLabel("Shipments value per day"), 2, 0)
		self.layout.addWidget(QLabel("Credits yield per hour"), 3, 0)
		self.layout.addWidget(QLabel("Hydrogen yield per hour"), 4, 0)
		self.layout.addWidget(QLabel("Global credits storage"), 5, 0)
		self.layout.addWidget(QLabel("Global hydrogen storage"), 6, 0)
		self.layout.addWidget(QLabel("Efficiency indicator"), 7, 0)

		cargoperhour = sum([planet.shipmentsPerHour() for planet in system.planets])
		self.layout.addWidget(QLabel(str(cargoperhour)), 0, 1)
		valueperhour = sum([planet.cargoPerHour() for planet in system.planets])
		valueperday = valueperhour * 24
		self.layout.addWidget(QLabel(str(valueperhour)), 1, 1)
		self.layout.addWidget(QLabel(str(valueperday)), 2, 1)
		creditsperhour = sum([planet.creditsPerHour() for planet in system.planets])
		hydroperhour = sum([planet.hydrogenPerHour() for planet in system.planets])
		self.layout.addWidget(QLabel(str(creditsperhour)), 3, 1)
		self.layout.addWidget(QLabel(str(hydroperhour)), 4, 1)
		creditstorage = sum([planet.creditStorage() for planet in system.planets])
		hydrostorage = sum([planet.hydrogenStorage() for planet in system.planets])
		self.layout.addWidget(QLabel(str(creditstorage)), 5, 1)
		self.layout.addWidget(QLabel(str(hydrostorage)), 6, 1)
		self.layout.addWidget(QLabel(str(round(efficiency, 3))), 7, 1)

		self.closebutton = QPushButton("Close")
		self.closebutton.clicked.connect(self.accept)
		self.layout.addWidget(self.closebutton, 8, 0)
		self.setLayout(self.layout)
		self.exec_()
