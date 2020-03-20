import sys
import ippcode_bank as ib



class Frames:
	def __init__(self):
		self.stackFrame = []
		self.TF = None
		self.LF = None
		self.GF = []

	def pushFrame(self):
		if self.TF != None:
			self.stackFrame.append(self.TF)
			self.LF = self.TF
			self.TF = None
		else:
			raise ib.FrameError("Temporary frame 'TF' does not exist")

	def popFrame(self):
		if len(self.stackFrame) != 0:
			self.TF = self.stackFrame.pop(-1)
			if len(self.stackFrame) != 0:
				self.LF = self.stackFrame[-1]
			else:
				self.LF = None
		else:
			raise ib.FrameError("Could not execute POPFRAME, frame stack is already empty")

	def getFromGF(self,var):	#returns index if found + the found var and type, if not found returns -1
		if self.GF == []:
			return -1, []
		index = 0
		for name in self.GF:
			if var == name[1]:
				return index, name
			index += 1
		return -1, []		#dont forget to protect error cases

	def getFromLF(self,var):
		if self.LF == None:
			raise ib.FrameError("Local frame 'LF' does not exist")
		for name in self.LF:
			if name[1] == var:
				return index, name
			index += 1
		return -1, []		#dont forget to protect error cases

	def getFromTF(self,var):
		if self.TF == None:
			raise ib.FrameError("Temporary frame 'TF' does not exist")
		for name in self.TF:
			if name[1] == var:
				return index, name
			index += 1
		return -1, []		#dont forget to protect error cases



class Variables:
	def __init__(self):
		self.frames = Frames()

	def defVar(self, var):
		if var[0] == "GF":
			found, foundvar = self.frames.getFromGF(var[1])
			if found != -1:
				raise ib.SemanticsError("redefinition of var '{0}' in '{1}'".format(var[1], var[0]))  
			else:
				typeAndVar = ["noneType", var[1], "noValue"]
				self.frames.GF.append(typeAndVar)
		elif var[0] == "TF":
			found, foundvar = self.frames.getFromTF(var[1])
			if found != -1:
				raise ib.SemanticsError("redefinition of var '{0}' in '{1}'".format(var[1], var[0]))
			else:
				typeAndVar = ["noneType", var[1], "noValue"]
				self.frames.TF.append(typeAndVar)
		elif var[0] == "LF":
			found, foundvar = self.frames.getFromLF(var[1])
			if found != -1:
				raise ib.SemanticsError("redefinition of var '{0} in '{1}'".format(var[1], var[0]))
			else:
				typeAndVar = ["noneType", var[1], "noValue"]
				self.frames.LF.append(typeAndVar)

	def move(self, var, symb):
		found = False
		foundvar = []
		foundS = False
		foundSymb = []
		if var[0] == "GF":
			found, foundvar = self.frames.getFromGF(var[1])
			if found == -1:
				raise ib.UndefinedVar("var '{0}' in '{1}' is not defined".format(var[1], var[0]))  
		elif var[0] == "TF":
			found, foundvar = self.frames.getFromTF(var[1])
			if found == -1:
				raise ib.UndefinedVar("var '{0}' in '{1}' is not defined".format(var[1], var[0])) 
		elif var[0] == "LF":
			found, foundvar = self.frames.getFromLF(var[1])
			if found == -1:
				raise ib.UndefinedVar("var '{0}' in '{1}' is not defined".format(var[1], var[0])) 

		if symb[0] == 'var':
			symb = symb.split('@',1)
			if symb[0] == "GF":
				foundS, foundSymb = self.frames.getFromGF(var[1])
				if foundS == -1:
					raise ib.UndefinedVar("var '{0}' in '{1}' is not defined".format(symb[1], symb[0]))  
			elif symb[0] == "TF":
				foundS, foundSymb = self.frames.getFromTF(var[1])
				if foundS == -1:
					raise ib.UndefinedVar("var '{0}' in '{1}' is not defined".format(symb[1], symb[0])) 
			elif symb[0] == "LF":
				foundS, foundSymb = self.frames.getFromLF(var[1])
				if foundS == -1:
					raise ib.UndefinedVar("var '{0}' in '{1}' is not defined".format(symb[1], symb[0])) 
			if var[0] == "GF":
				self.frames.GF[found][0] = foundSymb[0]
				self.frames.GF[found][2] = foundSymb[2]
			elif var[0] == "TF":
				self.frames.TF[found][0] = foundSymb[0]
				self.frames.TF[found][2] = foundSymb[2]
			elif var[0] == "LF":
				self.frames.LF[found][0] = foundSymb[0]
				self.frames.LF[found][2] = foundSymb[2]
		else:
			if var[0] == "GF":
				self.frames.GF[found][0] = symb[0]
				self.frames.GF[found][2] = symb[1]
			elif var[0] == "TF":
				self.frames.TF[found][0] = symb[0]
				self.frames.TF[found][2] = symb[1]
			elif var[0] == "LF":
				self.frames.LF[found][0] = symb[0]
				self.frames.LF[found][2] = symb[1]




		