import sys
import ippcode_bank as ib




class Frames:
	def __init__(self):
		self.stackFrame = []
		self.tempFrame = None
		self.localFrame = None
		self.globalFrame = []

	def pushFrame(self):
		if self.tempFrame != None:
			self.stackFrame.append(self.tempFrame)
			self.localFrame = self.tempFrame
			self.tempFrame = None
		else:
			raise ib.FrameError("Temporary frame 'TF' does not exist")

	def popFrame(self):
		if len(self.stackFrame) != 0:
			self.tempFrame = self.stackFrame.pop(-1)	
			try:
				self.localFrame = self.stackFrame[-1]
			except IndexError:
				self.localFrame = None
		else:
			raise ib.FrameError("Could not execute POPFRAME, frame stack is already empty")

	def addGlobal(self):
		pass
	def addLocal(self):
		pass
	def addTemp(self):
		pass
	def getGlobal(self):
		pass
	def getLocal(self):
		pass
	def getTemp(self):
		pass

class Variables:
	def __init__(self):
		