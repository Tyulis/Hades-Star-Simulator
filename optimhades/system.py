# -*- coding:utf-8 -*-

import json

sec = 1
mn = 60 * sec
hour = 60 * mn
day = 24 * hour

PLANET_UPGRADE_COSTS = (
	None,
	50, 200, 500, 1000, 2000,
	4000, 8000, 10000, 20000,
	30000, 40000, 50000, 75000,
	100000, 125000, 150000, 175000,
	200000, 250000, 300000, 400000,
	500000, 600000, 800000, 1000000,
	1250000, 1500000, 1750000, 2000000,
	2250000, 2500000, 2750000, 3000000,
	3500000, 4000000, 4500000, 5000000,
	5500000, 6000000,
)

PLANET_UPGRADE_TIMES = (
	None, 0,
	10, 30, 2*mn, 5*mn, 30*mn,
	1*hour, 4*hour, 8*hour, 13*hour+33*mn,
	1*day, 1.5*day, 2*day, 2.5*day, 3*day, 3.5*day,
	4*day, 4.5*day, 5*day, 5.5*day, 6*day, 6.5*day,
	7*day, 7.5*day, 8*day, 8.5*day, 9*day, 9.5*day,
	10*day, 10.5*day, 11*day, 11.5*day,
	12*day, 12.5*day, 13*day, 13.5*day,
	14*day, 14*day, 14*day, 14*day,
)

PLANET_CREDITS_STORAGE = (
	None,
	1000, 1400, 1800, 3000, 4000,
	5000, 6000, 7500, 10000, 13000,
	16000, 20000, 24000, 28000, 35000,
	45000, 65000, 90000, 130000, 170000,
	210000, 250000, 290000, 330000, 370000,
	410000, 450000, 490000, 530000, 570000,
	610000, 650000, 690000, 730000, 770000,
	810000, 850000, 850000, 850000, 850000,
)

PLANET_HYDROGEN_STORAGE = (
	None,
	200, 260, 340, 450, 570,
	750, 960, 1250, 1600, 2100,
	2750, 3600, 5000, 7000, 9000,
	11000, 13000, 15000, 17000, 19000,
	20000, 21000, 22000, 23000, 24000,
	25000, 26000, 27000, 28000, 29000,
	30000, 31000, 32000, 33000, 34000,
	35000, 36000, 37000, 38000, 39000,
)


PLANET_MAX_LEVELS = {1: 15, 2: 20, 3: 30, 4: 40}
PLANET_TIERS = {15: 1, 20: 2, 30: 3, 40: 4}

class Planet (object):
	def __init__(self, tier, level, position):
		self.tier = tier
		self.level = level
		self.position = position

	def upgradeCost(self, level=None):
		if level is None:
			level = self.level
		if level >= PLANET_MAX_LEVELS[self.tier]:
			return 0
		return PLANET_UPGRADE_COSTS[level]

	def upgradeBreakEven(self, level=None):
		if level is None:
			level = self.level
		if level >= PLANET_MAX_LEVELS[self.tier]:
			return 0
		shipdiff = (self.SHIPMENT_YIELD[self.tier][self.level + 1] - self.SHIPMENT_YIELD[self.tier][self.level]) / hour
		creditdiff = (self.CREDITS_YIELD[self.tier][self.level + 1] - self.CREDITS_YIELD[self.tier][self.level]) / hour
		cost = self.upgradeCost(level)
		return cost / (creditdiff + shipdiff)

	def cargoPerHour(self, level=None):
		if level is None:
			level = self.level
		return self.SHIPMENT_YIELD[self.tier][self.level]

	def creditsPerHour(self, level=None):
		if level is None:
			level = self.level
		return self.CREDITS_YIELD[self.tier][self.level]

	def hydrogenPerHour(self, level=None):
		if level is None:
			level = self.level
		return self.HYDROGEN_YIELD[self.tier][self.level]

	def creditStorage(self, level=None):
		if level is None:
			level = self.level
		return PLANET_CREDITS_STORAGE[self.level]

	def hydrogenStorage(self, level=None):
		if level is None:
			level = self.level
		return PLANET_HYDROGEN_STORAGE[self.level]

	def maxShipments(self):
		return self.SHIPMENT_STORAGE[self.tier]

	def shipmentsPerHour(self):
		return self.SHIPMENT_PER_HOUR[self.tier]

class DesertPlanet (Planet):
	type = "Desert"
	SHIPMENT_STORAGE = {1: 3*10, 3: 24, 4: 36}
	SHIPMENT_PER_HOUR = {1: 3*0.8, 3: 2, 4: 3}
	SHIPMENT_YIELD = {
		1: (
			None, 87, 94, 102, 110,
			119, 128, 138, 149, 161,
			174, 188, 203, 220, 237,
			256,
		), 3: (
			None,
			93, 101, 109, 118, 127,
			137, 148, 160, 173, 187,
			202, 218, 235, 254, 275,
			297, 312, 334, 357, 382,
			409, 438, 468, 501, 536,
			574, 614, 657, 703, 752,
		), 4: (
			None,
			106, 114, 123, 133, 143,
			156, 168, 181, 196, 212,
			229, 247, 267, 288, 311,
			336, 354, 378, 405, 433,
			465, 496, 531, 568, 608,
			650, 696, 745, 797, 853,
			912, 976, 1046, 1120, 1196,  #From lv33, estimations, for all planets
			1280, 0000, 0000, 0000, 0000
		),
	}

	CREDITS_YIELD = {
		1: (
			None,
			0, 1, 2, 4, 5, 7, 8, 10, 12, 14,
			17, 19, 21, 24, 26,
		), 3: (
			None,
			0, 1, 3, 4, 6, 8, 9, 12, 14, 16,
			20, 22, 24, 28, 30, 33, 36, 40, 44, 48,
			48, 52, 52, 56, 60, 60, 64, 64, 68, 68,
		), 4: (
			None,
			0, 1, 3, 5, 7, 9, 10, 13, 16, 18,
			22, 25, 27, 31, 34, 37, 41, 45, 49, 54,
			54, 58, 58, 63, 63, 67, 67, 72, 72, 76,
			76, 81, 81, 85, 85, 90, 90, 95, 95, 100,
		),
	}

	HYDROGEN_YIELD = {
		1: (
			None,
			8, 8, 8, 8, 8, 9, 9, 10, 10, 11,
			11, 12, 12, 13, 13,
		), 3: (
			None,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
		), 4: (
			None,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
		),
	}

class LavaPlanet (Planet):
	type = "Lava"
	SHIPMENT_STORAGE = {1: 2*15, 3: 24, 4: 36}
	SHIPMENT_PER_HOUR = {1: 2*1.2, 3: 2, 4: 3.2}
	SHIPMENT_YIELD = {
		1: (
			None,
			112, 121, 131, 141, 153,
			165, 178, 192, 208, 224,
			242, 262, 283, 305, 330,
		), 3: (
			None,
			118, 128, 138, 149, 161,
			174, 188, 203, 219, 237,
			256, 276, 298, 322, 348,
			376, 395, 423, 453, 484,
			518, 555, 593, 635, 679,
			727, 778, 832, 891, 953,
		), 4: (
			None,
			125, 135, 145, 157, 170,
			183, 198, 214, 231, 249,
			269, 291, 314, 339, 366,
			396, 416, 445, 477, 510,
			546, 584, 625, 668, 715,
			765, 819, 876, 938, 1003,
			1073, 1149, 1229, 1317, 1409,
			1506, 1611, 0000, 0000, 0000,
		),
	}

	CREDITS_YIELD = {
		1: (
			None,
			0, 1, 2, 4, 5, 7, 8, 10, 12, 14,
			17, 19, 21, 24, 26,
		), 3: (
			None,
			0, 1, 3, 4, 6, 8, 9, 12, 14, 16,
			20, 22, 24, 28, 30, 33, 36, 40, 44, 48,
			48, 52, 52, 56, 56, 60, 60, 64, 64, 68,
		), 4: (
			None,
			0, 1, 3, 5, 7, 9, 10, 13, 16, 18,
			22, 25, 27, 31, 34, 37, 41, 45, 49, 54,
			54, 58, 58, 63, 63, 67, 67, 72, 72, 76,
			76, 81, 81, 85, 85, 90, 90, 95, 95, 100,
		),
	}

	HYDROGEN_YIELD = {
		1: (
			None,
			8, 8, 8, 8, 8, 9, 9, 10, 10, 11,
			11, 12, 12, 13, 13,
		), 3: (
			None,
			9, 9, 9, 9, 9, 10, 10, 12, 12, 13,
			13, 14, 14, 15, 15, 16, 16, 18, 18, 19,
			19, 20, 20, 21, 21, 22, 22, 24, 24, 24,
		), 4: (
			None,
			11, 11, 11, 11, 11, 12, 12, 14, 14, 15,
			15, 16, 16, 18, 18, 19, 19, 21, 21, 22,
			22, 23, 23, 25, 25, 26, 26, 27, 27, 28,
			28, 28, 28, 28, 28, 28, 28, 28, 28, 28,
		),
	}

class WaterPlanet (Planet):
	type = "Water"
	SHIPMENT_STORAGE = {1: 2*18, 3: 24, 4: 38}
	SHIPMENT_PER_HOUR = {1: 2*1.4, 3: 2, 4: 3.2}
	SHIPMENT_YIELD = {
		1: (
			None,
			118, 128, 138, 149, 161,
			174, 188, 203, 219, 237,
			256, 276, 298, 322, 348,
		), 3: (
			None,
			125, 135, 145, 157, 170,
			183, 198, 214, 231, 249,
			269, 291, 314, 339, 366,
			396, 416, 445, 477, 510,
			546, 584, 625, 668, 715,
			765, 819, 876, 938, 1003,
		), 4: (
			None,
			131, 141, 153, 165, 178,
			192, 208, 224, 242, 262,
			283, 305, 330, 356, 385,
			415, 437, 468, 500, 535,
			573, 613, 656, 702, 751,
			804, 860, 920, 000, 1053,
			0000, 1206, 0000, 0000, 1478,
			1581, 0000, 0000, 0000, 0000,
		),
	}

	CREDITS_YIELD = {
		1: (
			None,
			1, 2, 4, 6, 8, 10, 12, 15, 18, 21,
			25, 28, 31, 35, 38,
		), 3: (
			None,
			1, 2, 4, 6, 8, 10, 12, 15, 18, 21,
			25, 28, 31, 35, 38, 42, 46, 50, 55, 60,
			60, 65, 65, 70, 70, 75, 75, 80, 80, 85,
		), 4: (
			None,
			1, 2, 4, 6, 8, 10, 12, 15, 18, 21,
			25, 28, 31, 35, 38, 42, 46, 50, 55, 60,
			60, 65, 65, 70, 70, 75, 75, 80, 80, 85,
			85, 90, 90, 95, 95, 100, 100, 105, 105, 110,
		),
	}

	HYDROGEN_YIELD = {
		1: (
			None,
			16, 16, 16, 16, 16, 18, 18, 20, 20, 22,
			22, 24, 24, 26, 26,
		), 3: (
			None,
			16, 16, 16, 16, 16, 18, 18, 20, 20, 22,
			22, 24, 24, 26, 26, 28, 28, 30, 30, 32,
			32, 34, 34, 36, 36, 38, 38, 40, 40, 40,
		), 4: (
			None,
			16, 16, 16, 16, 16, 18, 18, 20, 20, 22,
			22, 24, 24, 26, 26, 28, 28, 30, 30, 32,
			32, 34, 34, 36, 36, 38, 38, 40, 40, 40,
			40, 40, 40, 40, 40, 40, 40, 40, 40, 40,
		),
	}

class TerranPlanet (Planet):
	type = "Terran"
	SHIPMENT_STORAGE = {1: 18, 3: 27, 4: 35}
	SHIPMENT_PER_HOUR = {1: 1.5, 3: 2.2, 4: 3}
	SHIPMENT_YIELD = {
		1: (
			None,
			143, 155, 167, 181, 195,
			211, 227, 246, 265, 287,
			310, 334, 361, 390, 421,
		), 3: (
			None,
			150, 162, 174, 188, 204,
			220, 237, 256, 277, 299,
			323, 349, 377, 407, 440,
			475, 500, 535, 572, 612,
			655, 701, 750, 802, 858,
			919, 983, 1052, 1125, 1204,
		), 4: (
			None,
			156, 168, 182, 196, 212,
			229, 247, 267, 289, 312,
			337, 363, 393, 424, 458,
			495, 520, 557, 596, 638,
			682, 730, 781, 836, 894,
			957, 1024, 1095, 0000, 1254,
			0000, 1436, 0000, 1644, 1759,
			0000, 0000, 0000, 0000, 0000,
		),
	}

	CREDITS_YIELD = {
		1: (
			None,
			1, 2, 4, 6, 8, 10, 12, 15, 18, 21,
			25, 28, 31, 35, 38,
		), 3: (
			None,
			1, 2, 4, 6, 8, 10, 12, 15, 18, 21,
			25, 28, 31, 35, 38, 42, 46, 50, 55, 60,
			60, 65, 65, 70, 70, 75, 75, 80, 80, 85,
		), 4: (
			None,
			1, 2, 4, 6, 8, 10, 12, 15, 18, 21,
			25, 28, 31, 35, 38, 42, 46, 50, 55, 60,
			60, 65, 65, 70, 70, 75, 75, 80, 80, 85,
			85, 90, 90, 95, 95, 100, 100, 105, 105, 110,
		),
	}

	HYDROGEN_YIELD = {
		1: (
			None,
			16, 16, 16, 16, 16, 18, 18, 20, 20, 22,
			22, 24, 24, 26, 26,
		), 3: (
			None,
			16, 16, 16, 16, 16, 18, 18, 20, 20, 22,
			22, 24, 24, 26, 26, 28, 28, 30, 30, 32,
			32, 34, 34, 36, 36, 38, 38, 40, 40, 40,
		), 4: (
			None,
			16, 16, 16, 16, 16, 18, 18, 20, 20, 22,
			22, 24, 24, 26, 26, 28, 28, 30, 30, 32,
			32, 34, 34, 36, 36, 38, 38, 40, 40, 40,
			40, 40, 40, 40, 40, 40, 40, 40, 40, 40,
		),
	}

class GasPlanet (Planet):
	type = "Gas"
	SHIPMENT_STORAGE = {2: 22, 4: 40}
	SHIPMENT_PER_HOUR = {2: 1.8, 4: 3.2}
	SHIPMENT_YIELD = {
		2: (
			None,
			150, 162, 174, 188, 204,
			220, 237, 256, 277, 299,
			323, 349, 377, 407, 440,
			475, 500, 535, 572, 612,
		), 4: (
			None,
			156, 168, 182, 196, 212,
			229, 247, 267, 289, 312,
			337, 363, 393, 424, 458,
			495, 520, 557, 596, 638,
			682, 730, 781, 836, 894,
			957, 1024, 1095, 1172, 1254,
			0000, 1436, 0000, 0000, 0000,
			0000, 2014, 0000, 0000, 0000,
		),
	}

	CREDITS_YIELD = {
		2: (
			None,
			1, 2, 4, 6, 8, 10, 12, 15, 18, 21,
			25, 28, 31, 35, 38, 42, 46, 50, 55, 60,
		), 4: (
			None,
			1, 2, 4, 6, 8, 10, 12, 15, 18, 21,
			25, 28, 31, 35, 38, 42, 46, 50, 55, 60,
			60, 65, 65, 70, 70, 75, 75, 80, 80, 85,
			85, 90, 90, 95, 95, 100, 100, 105, 105, 110,
		),
	}

	HYDROGEN_YIELD = {
		2: (
			None,
			16, 16, 16, 16, 16, 18, 18, 20, 20, 22,
			22, 24, 24, 26, 26, 28, 28, 30, 30, 32,
		), 4: (
			None,
			16, 16, 16, 16, 16, 18, 18, 20, 20, 22,
			22, 24, 24, 26, 26, 28, 28, 30, 30, 32,
			32, 34, 34, 36, 36, 38, 38, 40, 40, 40,
			40, 40, 40, 40, 40, 40, 40, 40, 40, 40,
		),
	}

class IcePlanet (Planet):
	type = "Ice"
	SHIPMENT_STORAGE = {4: 50}
	SHIPMENT_PER_HOUR = {4: 3.2}
	SHIPMENT_YIELD = {
		4: (
			None,
			000, 000, 000, 000, 000,
			000, 000, 000, 000, 000,
			377, 000, 000, 000, 513,
			554, 583, 624, 667, 714,
			764, 818, 875, 936, 1002,
			1072, 1147, 1227, 1313, 1405,
			1503, 1608, 1721, 0000, 1970,
			2108, 0000, 0000, 0000, 0000,
		),
	}

	CREDITS_YIELD = {
		4: (
			None,
			00, 00, 00, 00, 00, 00, 00, 00, 00, 00,
			00, 00, 00, 00, 38, 42, 46, 50, 55, 60,
			60, 65, 65, 70, 70, 75, 75, 80, 80, 85,
			85, 90, 90, 95, 95, 100, 100, 105, 105, 110,
		),
	}

	HYDROGEN_YIELD = {
		4: (
			None,
			16, 16, 16, 16, 16, 18, 18, 20, 20, 22,
			22, 24, 24, 26, 26, 28, 28, 30, 30, 32,
			32, 34, 34, 36, 36, 38, 38, 40, 40, 40,
			40, 40, 40, 40, 40, 40, 40, 40, 40, 40,
		),
	}


class TradeStation (Planet):
	type = "Station"
	SHIPMENT_STORAGE = {1: 18}
	SHIPMENT_PER_HOUR = {1: 1}
	SHIPMENT_YIELD = {
		1: (
			None,
			208, 291, 408, 571, 800,
			1120, 1568, 2196, 3074, 4304,
			4304, 4304, 4304, 4304, 4304,
		),
	}

	CREDITS_YIELD = {
		1: (
			None,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0,
		),
	}

	HYDROGEN_YIELD = {
		1: (
			None,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0,
		),
	}

PLANET_TYPES = {
	"Desert": DesertPlanet, "Lava": LavaPlanet,
	"Water": WaterPlanet, "Terran": TerranPlanet,
	"Gas": GasPlanet, "Ice": IcePlanet,
	"Station": TradeStation,
}

PLANET_TYPE_TIERS = {
	"Desert": (1, 3, 4), "Lava": (1, 3, 4),
	"Water": (1, 3, 4), "Terran": (1, 3, 4),
	"Gas": (2, 4), "Ice": (4, ),
	"Station": (1, ),
}

def makePlanet(type, tier, level, position):
	return PLANET_TYPES[type](tier, level, position)

def changePlanetType(planet, type):
	return PLANET_TYPES[type](planet.tier, planet.level, planet.position)


class WarpLaneHub (object):
	def __init__(self, position, link=None):
		self.position = position
		self.link = link

	def __eq__(self, hub):
		return hub.position == self.position


class System (object):
	def __init__(self, planets=[], hubs=[]):
		self.filename = None
		self.planets = planets
		self.hubs = hubs

	@classmethod
	def load(cls, filename):
		instance = cls()
		instance.filename = filename
		with open(filename, "r") as f:
			data = json.load(f)
		for dic in data["planets"]:
			instance.planets.append(makePlanet(dic["type"], dic["tier"], dic["level"], dic["position"]))
		for dic in data["hubs"]:
			instance.hubs.append(WarpLaneHub(dic["position"]))
		for i, dic in enumerate(data["hubs"]):
			if dic["link"] != -1:
				instance.hubs[i].link = instance.hubs[dic["link"]]
		return instance

	def save(self):
		dic = {
			"planets": [{"type": planet.type, "tier": planet.tier, "level": planet.level, "position": planet.position} for planet in self.planets],
			"hubs": [{"position": hub.position, "link": (self.hubs.index(hub.link) if hub.link is not None else -1)} for hub in self.hubs],
		}
		with open(self.filename, "w") as f:
			json.dump(dic, f)
