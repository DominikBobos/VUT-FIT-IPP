import sys
import ippcode_bank as ib

class Dependencies:
	def __init__(self):
		self.stackFrame = []
		self.TF = None
		self.LF = None
		self.GF = []
		self.dataStack = []

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

	def defVar(self, var):
		if var[0] == "GF":
			found, foundvar = self.getFromGF(var[1])
			if found != -1:
				raise ib.SemanticsError("redefinition of var '{0}' in '{1}'".format(var[1], var[0]))  
			else:
				typeAndVar = ["", var[1], "noValue"]
				self.GF.append(typeAndVar)
		elif var[0] == "TF":
			found, foundvar = self.getFromTF(var[1])
			if found != -1:
				raise ib.SemanticsError("redefinition of var '{0}' in '{1}'".format(var[1], var[0]))
			else:
				typeAndVar = ["", var[1], "noValue"]
				self.TF.append(typeAndVar)
		elif var[0] == "LF":
			found, foundvar = self.getFromLF(var[1])
			if found != -1:
				raise ib.SemanticsError("redefinition of var '{0} in '{1}'".format(var[1], var[0]))
			else:
				typeAndVar = ["", var[1], "noValue"]
				self.LF.append(typeAndVar)

	def foundVar(self, var, symbBool):
		found = -1
		foundVar = []
		if symbBool == True:
			if var[0] == 'var':
				var = var[1].split('@',1)
			else:
				foundVar = [var[0], [], var[1]]
				return found, foundVar

		if var[0] == "GF":
			found, foundVar = self.getFromGF(var[1])
			if found == -1:
				raise ib.UndefinedVar("var '{0}' in '{1}' is not defined".format(var[1], var[0]))  
		elif var[0] == "TF":
			found, foundVar = self.getFromTF(var[1])
			if found == -1:
				raise ib.UndefinedVar("var '{0}' in '{1}' is not defined".format(var[1], var[0])) 
		elif var[0] == "LF":
			found, foundVar = self.getFromLF(var[1])
			if found == -1:
				raise ib.UndefinedVar("var '{0}' in '{1}' is not defined".format(var[1], var[0]))
		return found, foundVar

	def setTypeValue(self, frame, index, typeVar, value):
		if frame == "GF":
			self.GF[index][0] = typeVar
			self.GF[index][2] = value
		elif frame == "TF":
			self.TF[index][0] = typeVar
			self.TF[index][2] = value
		elif frame == "LF":
			self.LF[index][0] = typeVar
			self.LF[index][2] = value

	def move(self, var, symb):
		varIndex, varFound = self.foundVar(var, False)
		symbIndex, symbFound = self.foundVar(symb, True)
		self.setTypeValue(var[0],varIndex,symbFound[0], symbFound[2])

	def calculate(self, op, var, symb1, symb2):
		varIndex, varFound = self.foundVar(var, False)
		symb1Index, symb1Found = self.foundVar(symb1, True)
		symb2Index, symb2Found = self.foundVar(symb2, True)
		if symb1Found[0] != 'int': 
			if symb1Found[1] == []:
				varOrSymb = 'symb'
			else:
				varOrSymb = 'var: ' + symb1Found[1]
			raise ib.WrongArgTypes(
				"operand ({3})'{0}' of type '{1}' is not of the correct type for operation '{2}'".format(
				symb1Found[2], symb1Found[0], op, varOrSymb))
		if symb2Found[0] != 'int':
			if symb2Found[1] == []:
				varOrSymb = 'symb'
			else:
				varOrSymb = 'var: ' + symb2Found[1]
			raise ib.WrongArgTypes(
			"operand ({3})'{0}' of type '{1}' is not of the correct type for operation '{2}'".format(
				symb2Found[2], symb2Found[0], op, varOrSymb))
		
		if op == 'ADD':
			self.setTypeValue(var[0],varIndex, 'int', symb1Found[2] + symb2Found[2])
		elif op == 'SUB':
			self.setTypeValue(var[0],varIndex, 'int', symb1Found[2] - symb2Found[2])
		elif op == 'MUL':
			self.setTypeValue(var[0],varIndex, 'int', symb1Found[2] * symb2Found[2])
		elif op == 'IDIV':
			try:
				self.setTypeValue(var[0],varIndex, 'int', symb1Found[2] // symb2Found[2])
			except ZeroDivisionError:
				raise ib.WrongValue("Zero division error")

	def conditions(self, op, var, symb1, symb2):
		varIndex, varFound = self.foundVar(var, False)
		symb1Index, symb1Found = self.foundVar(symb1, True)
		symb2Index, symb2Found = self.foundVar(symb2, True)	

		if symb1Found[0] != symb2Found[0] or (symb1Found[0] == 'nil' or symb2Found[0] == 'nil'):
			if op == 'EQ' and (symb1Found[0] == 'nil' or symb2Found[0] == 'nil'):
				pass
			else:
				raise ib.WrongArgTypes(
				"different types for relational instructions, '{0}'('{1}') '{2}'('{3}')".format(
					symb1Found[2],symb1Found[0],symb2Found[2], symb2Found[0]))
		if symb1Found[0] == 'bool':
			if symb1Found[2] == 'true':
				symb1Found[2] == True
			else:
				symb1Found[2] == False
		if symb2Found[0] == 'bool':
			if symb2Found[2] == 'true':
				symb2Found[2] == True
			else:
				symb2Found[2] == False
		if op == 'LT':
			if symb1Found[2] < symb2Found[2]:
				self.setTypeValue(var[0],varIndex, 'bool', 'true')
			else:
				self.setTypeValue(var[0],varIndex, 'bool', 'false')
		elif op == 'GT':
			if symb1Found[2] > symb2Found[2]:
				self.setTypeValue(var[0],varIndex, 'bool', 'true')
			else:
				self.setTypeValue(var[0],varIndex, 'bool', 'false')
		elif op == 'EQ':
			if symb1Found[2] == 'nil' or symb2Found[2] == 'nil':
				if symb1Found[2] == symb2Found[2]:
					self.setTypeValue(var[0],varIndex, 'bool', 'true')
				else:
					self.setTypeValue(var[0],varIndex, 'bool', 'false')	
			else:
				if symb1Found[2] == symb2Found[2]:
					self.setTypeValue(var[0],varIndex, 'bool', 'true')
				else:
					self.setTypeValue(var[0],varIndex, 'bool', 'false')
	
	def logical(self, op, var, symb1, symb2 = []):
		varIndex, varFound = self.foundVar(var, False)
		symb1Index, symb1Found = self.foundVar(symb1, True)
		symb2Found = ['bool', []]	#just because of 'NOT' uses only 2 args
		if op != 'NOT':
			symb2Index, symb2Found = self.foundVar(symb2, True)	
		if op == 'NOT' and symb1Found[0] != 'bool':
			raise ib.WrongArgTypes(
			"Logical operations need bool type, not '{0}'('{1}')".format(
				symb1Found[2],symb1Found[0]))
		elif symb1Found[0] != 'bool' or symb2Found[0] != 'bool':
			raise ib.WrongArgTypes(
			"Logical operations need bool type, not '{0}'('{1}') '{2}'('{3}')".format(
				symb1Found[2],symb1Found[0],symb2Found[2], symb2Found[0]))	
		if op == 'AND':
			if symb1Found[2] == 'true' and symb2Found[2] == 'true':
				self.setTypeValue(var[0],varIndex, 'bool', 'true')
			else:
				self.setTypeValue(var[0],varIndex, 'bool', 'false')	
		elif op == 'OR':
			if symb1Found[2] == 'true' or symb2Found[2] == 'true':
				self.setTypeValue(var[0],varIndex, 'bool', 'true')
			else:
				self.setTypeValue(var[0],varIndex, 'bool', 'false')	
		elif op == 'NOT':
			if symb1Found[2] == 'true':
				self.setTypeValue(var[0],varIndex, 'bool', 'false')
			else:
				self.setTypeValue(var[0],varIndex, 'bool', 'true')
	
	#JUMPIFEQ and JUMPIFNEQ implementation, returns true or false depends on condition 
	def condJumps(self, op, symb1, symb2):
		symb1Index, symb1Found = self.foundVar(symb1, True)
		symb2Index, symb2Found = self.foundVar(symb2, True)	
		if symb1Found[0] != symb2Found[0]:
			if symb1Found[0] == 'nil' or symb2Found[0] == 'nil':
				pass
			else:
				raise ib.WrongArgTypes(
				"different types for relational instructions, '{0}'('{1}') '{2}'('{3}')".format(
					symb1Found[2],symb1Found[0],symb2Found[2], symb2Found[0]))	
		if symb1Found[2] == 'nil' or symb2Found[2] == 'nil':
			if symb1Found[2] == symb2Found[2]:
				if op == 'JUMPIFEQ':
					return True
				else:
					return False
			else:
				if op == 'JUMPIFEQ':
					return False
				else:
					return True
		else:
			if symb1Found[2] == symb2Found[2]:
				if op == 'JUMPIFEQ':
					return True
				else:
					return False
			else:
				if op == 'JUMPIFEQ':
					return False
				else:
					return True

	#adds data from symb to dataStack
	def pushs(self, symb):
		symbIndex, symbFound = self.foundVar(symb, True)
		appendSymb = [symbFound[0], symbFound[2]]
		self.dataStack.append(appendSymb)

	#pops the top of the dataStack to variable var
	def pops(self, var):
		if self.dataStack == []:
			raise ib.MissingValue("instruction POPS cannot be executed: data stack is empty")
		varIndex, varFound = self.foundVar(var, False)
		popSymb = self.dataStack.pop(-1)
		self.setTypeValue(var[0], varIndex, popSymb[0], popSymb[1])

	#reads input data from stdin via input() or via file 
	#from sys.arg --input and saves the value to the var
	def read(self, var, typeValue, inputFile, inputBool):
		varIndex, varFound = self.foundVar(var, False)
		try:
			if inputBool == True:
				readValue = open(inputFile, "r")
				readValue = readValue.read()
			else: 
				readValue = input()
			try:
				if typeValue == 'int':
					self.setTypeValue(var[0],varIndex, 'int', int(readValue))
				elif typeValue == 'string':
					self.setTypeValue(var[0],varIndex, 'string', readValue)
				elif typeValue == 'bool':
					if readValue.upper() == 'TRUE':
						self.setTypeValue(var[0],varIndex, 'bool', 'true')
					else:
						self.setTypeValue(var[0],varIndex, 'bool', 'false')
			except ValueError:			#HERE BIG QUESTION ..mam tu dat nil@nil alebo chybu?!?!?!
				self.setTypeValue(var[0],varIndex, 'nil', 'nil')
		except EOFError:
			self.setTypeValue(var[0],varIndex, 'nil', 'nil')

	#prints value from symb to STDOUT 
	def write(self, symb):
		symbIndex, symbFound = self.foundVar(symb, True)
		if symbFound[0] == 'nil':
			print('',end='')
		elif symbFound[0] == 'bool':
			if symbFound[2] == 'true':
				print('true',end='')
			else:
				print('false',end='')
		elif symbFound[0] == 'int':
			print(symbFound[2],end='')
		elif symbFound[0] == 'string':
			print(symbFound[2],end='')

	#concatenation of symb1 and symb2, the result is saved to var. must be string type
	def concat(self, var, symb1, symb2):
		varIndex, varFound = self.foundVar(var, False)
		symb1Index, symb1Found = self.foundVar(symb1, True)
		symb2Index, symb2Found = self.foundVar(symb2, True)
		if symb1Found[0] == 'string' and symb2Found[0] == 'string':
			self.setTypeValue(var[0],varIndex, 'string', symb1[1] + symb2[1])
		else:
			raise ib.WrongArgTypes("CONCAT needs two string arguments.")

	def strlen(self,var,symb):
		varIndex, varFound = self.foundVar(var, False)
		symbIndex, symbFound = self.foundVar(symb, True)
		if symbFound[0] == 'string':
			self.setTypeValue(var[0],varIndex, 'int', len(symbFound[2]))
		else:
			raise ib.WrongArgTypes("STRLEN needs string argument.")

	def getchar(self, var, symb1, symb2):
		varIndex, varFound = self.foundVar(var, False)
		symb1Index, symb1Found = self.foundVar(symb1, True)
		symb2Index, symb2Found = self.foundVar(symb2, True)
		if symb1Found[0] == 'string' and symb2Found[0] == 'int':
			try:
				self.setTypeValue(var[0],varIndex, 'string', symb1Found[2][symb2Found[2]])
			except IndexError:
				raise ib.StringError("Index error, in function GETCHAR index '{0}' is out of range of '{1}'".format(
					symb2Found[2], symb1Found[2]))
		else:
			raise ib.WrongArgTypes("GETCHAR needs first argument string, second arguments int.")

	def setchar(self, var, symb1, symb2):
		varIndex, varFound = self.foundVar(var, False)
		symb1Index, symb1Found = self.foundVar(symb1, True)
		symb2Index, symb2Found = self.foundVar(symb2, True)
		if varFound[0] == 'string' and symb1Found[0] == 'int' and symb2Found[0] == 'string':
			try:
				result = varFound[2][:symb1Found[2]] + symb2Found[2][0] + varFound[2][symb1Found[2]+1:]
				self.setTypeValue(var[0], varIndex, 'string', result)
			except IndexError:
				raise ib.StringError("Index error, in function SETCHAR index '{0}' is out of range of '{1}'".format(
					symb1Found[2], varFound[2]))
		else:
			raise ib.WrongArgTypes(
				"SETCHAR needs variable of type string, first symbol of type int, second symbol of type string")

	def instrType(self, var, symb):
		varIndex, varFound = self.foundVar(var, False)
		symbIndex, symbFound = self.foundVar(symb, True)
		if symbFound[0] == '':
			self.setTypeValue(var[0], varIndex, 'string', '')
		elif symbFound[0] == 'nil':
			self.setTypeValue(var[0], varIndex, 'string', 'nil')
		elif symbFound[0] == 'bool':
			self.setTypeValue(var[0], varIndex, 'string', 'bool')
		elif symbFound[0] == 'int':
			self.setTypeValue(var[0], varIndex, 'string', 'int')
		elif symbFound[0] == 'string':
			self.setTypeValue(var[0], varIndex, 'string', 'string')

	def instrExit(self, symb):
		symbIndex, symbFound = self.foundVar(symb, True)

		if symbFound[0] != 'int' or (symbFound[2] < 0 or symbFound[2] > 49):
			raise ib.WrongValue("value for EXIT should be int in range 0-49, not '%s'" % symbFound[2])
		else:
			sys.exit(symbFound[2])

	def dprint(self, symb):
		symbIndex, symbFound = self.foundVar(symb, True)
		sys.stderr.write("%s" % symbFound[2])



		