import re
import xml.etree.ElementTree as elemTree
import ippcode_dependencies
import sys

TYPE = ['int', 'bool', 'string', 'float']	#nil is not here 

FRAME = ['LF', 'TF', 'GF']

INSTRUCTIONS =[ "MOVE", 
				"CREATEFRAME", "PUSHFRAME", "POPFRAME", 
				"DEFVAR", 
				"CALL", 
				"RETURN", 
				"PUSHS", "POPS", 
				"ADD", "SUB", 
				"MUL", "IDIV", "DIV", 
				"LT", "GT", "EQ", 
				"AND", "OR", "NOT", 
				"INT2CHAR", "STRI2INT", "INT2FLOAT", "FLOAT2INT", 
				"READ", "WRITE", 
				"CONCAT", "STRLEN", 
				"GETCHAR", "SETCHAR", 
				"TYPE", 
				"LABEL", 
				"JUMP", "JUMPIFEQ", "JUMPIFNEQ",
				"EXIT", 
				"DPRINT", 
				"BREAK",
				"CLEARS",
				"ADDS", "SUBS", "MULS", "IDIVS", "DIVS" 
				"LTS", "GTS", "EQS", 
				"ANDS", "ORS", "NOTS", 
				"INT2CHARS", "STRI2INTS", "INT2FLOATS", "FLOAT2INTS",
				"JUMPIFEQS", "JUMPIFNEQS" ]


'''
Class for Intterpret which does all the job
it is connected to ippcode_dependencies where are stored all the data and frames
This is the brain of the whole interpret
'''
class Interpret:
	def __init__(self):
		self.instructions = []	#stores all instructions from XMLfile in the right order
		self.labels = []		#stores all unique labels
		self.calls = []			#stack for CALL instruction
		self.labelIndex = []	#saves index of LABEL opcode in the correct order, so it saves time
		self.run = ippcode_dependencies.Dependencies()	
		self.instrCount = 0		#count of all executed instructions
		self.initVars = 0		#count of all initialized variables

	#checks if the instrucion has the right count of needed arguments
	def checkArgCount(self, instr, countGiven, neededCount):
		if countGiven == neededCount:
			pass
		else:
			raise ParseError("wrong number of arguments '{0}' needs '{1}' not '{2}' args".format(instr, neededCount, countGiven))

	#checks all instructions and their arguments, if they contain the right value
	def checkInstr(self, order, xmlInstr):
		for i in range(0,len(xmlInstr)):
			# ind = order[i][0] gives the index of instruction in xmlInstr in right order
			ind = order[i][0]
			if xmlInstr[ind][0].upper() not in INSTRUCTIONS:
				raise ParseError("'%s' instruction does not exist" % xmlInstr[ind][0])
			try:
				if xmlInstr[ind][0].upper() == "MOVE":
					self.checkArgCount(xmlInstr[ind][0], len(xmlInstr[ind]) - 1, 2)
					self.checkVar(xmlInstr[ind][1])
					self.checkSymb(xmlInstr[ind][2])
				elif xmlInstr[ind][0].upper() == "CREATEFRAME":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 0)
				elif xmlInstr[ind][0].upper() == "PUSHFRAME":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 0)
				elif xmlInstr[ind][0].upper() == "POPFRAME":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 0)
				elif xmlInstr[ind][0].upper() == "DEFVAR":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 1)
					self.checkVar(xmlInstr[ind][1])
				elif xmlInstr[ind][0].upper() == "CALL":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 1)
					self.checkLabel(xmlInstr[ind][1], -1)
				elif xmlInstr[ind][0].upper() == "RETURN":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 0)
				elif xmlInstr[ind][0].upper() == "PUSHS":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 1)
					self.checkSymb(xmlInstr[ind][1])
				elif xmlInstr[ind][0].upper() == "POPS":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 1)
					self.checkVar(xmlInstr[ind][1])
				elif xmlInstr[ind][0].upper() == "ADD":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 3)
					self.checkVar(xmlInstr[ind][1])
					self.checkSymb(xmlInstr[ind][2])
					self.checkSymb(xmlInstr[ind][3])
				elif xmlInstr[ind][0].upper() == "SUB":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 3)
					self.checkVar(xmlInstr[ind][1])
					self.checkSymb(xmlInstr[ind][2])
					self.checkSymb(xmlInstr[ind][3])
				elif xmlInstr[ind][0].upper() == "MUL":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 3)
					self.checkVar(xmlInstr[ind][1])
					self.checkSymb(xmlInstr[ind][2])
					self.checkSymb(xmlInstr[ind][3])
				elif xmlInstr[ind][0].upper() == "IDIV":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 3)
					self.checkVar(xmlInstr[ind][1])
					self.checkSymb(xmlInstr[ind][2])
					self.checkSymb(xmlInstr[ind][3])
				elif xmlInstr[ind][0].upper() == "DIV":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 3)
					self.checkVar(xmlInstr[ind][1])
					self.checkSymb(xmlInstr[ind][2])
					self.checkSymb(xmlInstr[ind][3])
				elif xmlInstr[ind][0].upper() == "LT":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 3)
					self.checkVar(xmlInstr[ind][1])
					self.checkSymb(xmlInstr[ind][2])
					self.checkSymb(xmlInstr[ind][3])
				elif xmlInstr[ind][0].upper() == "GT":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 3)
					self.checkVar(xmlInstr[ind][1])
					self.checkSymb(xmlInstr[ind][2])
					self.checkSymb(xmlInstr[ind][3])
				elif xmlInstr[ind][0].upper() == "EQ":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 3)
					self.checkVar(xmlInstr[ind][1])
					self.checkSymb(xmlInstr[ind][2])
					self.checkSymb(xmlInstr[ind][3])
				elif xmlInstr[ind][0].upper() == "AND":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 3)
					self.checkVar(xmlInstr[ind][1])
					self.checkSymb(xmlInstr[ind][2])
					self.checkSymb(xmlInstr[ind][3])
				elif xmlInstr[ind][0].upper() == "OR":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 3)
					self.checkVar(xmlInstr[ind][1])
					self.checkSymb(xmlInstr[ind][2])
					self.checkSymb(xmlInstr[ind][3])
				elif xmlInstr[ind][0].upper() == "NOT":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 2)
					self.checkVar(xmlInstr[ind][1])
					self.checkSymb(xmlInstr[ind][2])
				elif xmlInstr[ind][0].upper() == "INT2CHAR":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 2)
					self.checkVar(xmlInstr[ind][1])
					self.checkSymb(xmlInstr[ind][2])
				elif xmlInstr[ind][0].upper() == "FLOAT2INT":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 2)
					self.checkVar(xmlInstr[ind][1])
					self.checkSymb(xmlInstr[ind][2])
				elif xmlInstr[ind][0].upper() == "INT2FLOAT":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 2)
					self.checkVar(xmlInstr[ind][1])
					self.checkSymb(xmlInstr[ind][2])
				elif xmlInstr[ind][0].upper() == "STRI2INT":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 3)
					self.checkVar(xmlInstr[ind][1])
					self.checkSymb(xmlInstr[ind][2])
					self.checkSymb(xmlInstr[ind][3])
				elif xmlInstr[ind][0].upper() == "READ":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 2)
					self.checkVar(xmlInstr[ind][1])
					self.checkType(xmlInstr[ind][2])
				elif xmlInstr[ind][0].upper() == "WRITE":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 1)
					self.checkSymb(xmlInstr[ind][1])
				elif xmlInstr[ind][0].upper() == "CONCAT":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 3)
					self.checkVar(xmlInstr[ind][1])
					self.checkSymb(xmlInstr[ind][2])
					self.checkSymb(xmlInstr[ind][3])
				elif xmlInstr[ind][0].upper() == "STRLEN":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 2)
					self.checkVar(xmlInstr[ind][1])
					self.checkSymb(xmlInstr[ind][2])
				elif xmlInstr[ind][0].upper() == "GETCHAR":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 3)
					self.checkVar(xmlInstr[ind][1])
					self.checkSymb(xmlInstr[ind][2])
					self.checkSymb(xmlInstr[ind][3])
				elif xmlInstr[ind][0].upper() == "SETCHAR":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 3)
					self.checkVar(xmlInstr[ind][1])
					self.checkSymb(xmlInstr[ind][2])
					self.checkSymb(xmlInstr[ind][3])
				elif xmlInstr[ind][0].upper() == "TYPE":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 2)
					self.checkVar(xmlInstr[ind][1])
					self.checkSymb(xmlInstr[ind][2])
				elif xmlInstr[ind][0].upper() == "LABEL":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 1)
					self.checkLabel(xmlInstr[ind][1], i)
				elif xmlInstr[ind][0].upper() == "JUMP":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 1)
					self.checkLabel(xmlInstr[ind][1], -1)
				elif xmlInstr[ind][0].upper() == "JUMPIFEQ":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 3)
					self.checkLabel(xmlInstr[ind][1], -1)
					self.checkSymb(xmlInstr[ind][2])
					self.checkSymb(xmlInstr[ind][3])
				elif xmlInstr[ind][0].upper() == "JUMPIFNEQ":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 3)
					self.checkLabel(xmlInstr[ind][1], -1)
					self.checkSymb(xmlInstr[ind][2])
					self.checkSymb(xmlInstr[ind][3])
				elif xmlInstr[ind][0].upper() == "EXIT":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 1)
					self.checkSymb(xmlInstr[ind][1])
				elif xmlInstr[ind][0].upper() == "DPRINT":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 1)
					self.checkSymb(xmlInstr[ind][1])
				elif xmlInstr[ind][0].upper() == "BREAK":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 0)
				elif xmlInstr[ind][0].upper() == "CLEARS":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 0)
				elif xmlInstr[ind][0].upper() == "ADDS":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 0)
				elif xmlInstr[ind][0].upper() == "SUBS":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 0)
				elif xmlInstr[ind][0].upper() == "MULS":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 0)
				elif xmlInstr[ind][0].upper() == "DIVS":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 0)
				elif xmlInstr[ind][0].upper() == "IDIVS":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 0)
				elif xmlInstr[ind][0].upper() == "LTS":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 0)
				elif xmlInstr[ind][0].upper() == "GTS":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 0)
				elif xmlInstr[ind][0].upper() == "EQS":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 0)
				elif xmlInstr[ind][0].upper() == "ANDS":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 0)
				elif xmlInstr[ind][0].upper() == "ORS":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 0)
				elif xmlInstr[ind][0].upper() == "NOTS":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 0)
				elif xmlInstr[ind][0].upper() == "INT2CHARS":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 0)
				elif xmlInstr[ind][0].upper() == "STRI2INTS":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 0)
				elif xmlInstr[ind][0].upper() == "INT2FLOATS":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 0)
				elif xmlInstr[ind][0].upper() == "FLOAT2INTS":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 0)
				elif xmlInstr[ind][0].upper() == "JUMPIFEQS":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 1)
					self.checkLabel(xmlInstr[ind][1], -1)
				elif xmlInstr[ind][0].upper() == "JUMPIFNEQS":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 1)
					self.checkLabel(xmlInstr[ind][1], -1)
				temp = [xmlInstr[order[i][0]][0], xmlInstr[order[i][0]][1:]]
				#appends instructions with arguments in the right order 
				self.instructions.append(temp)
			except IndexError:
				raise ParseError("wrong arguments for instruction '%s'" % xmlInstr[ind][0])

	def checkVar(self, arg):
		if arg[0] != 'var' :
			raise ParseError("variable should have been 'var' not '%s'" % arg[0])
		try:
			arg = arg[1].split('@',1)
		except ValueError:
			raise ParseError("missing @ after frame")

		if arg[0] not in FRAME:
			raise ParseError("wrong frame: %s" % arg[0])

		if not re.match(r"^[a-zá-žA-ZÁ-Ž_\-$&%*?!][\w\-$&%*?!]*$", arg[1]):
			raise ParseError("variable '%s' is invalid" % arg[1])

	def checkSymb(self, arg):
		if arg[0] == 'var':
			self.checkVar(arg)
		elif arg[0] == 'nil':
			if arg[1] != 'nil':
				raise ParseError("invalid 'nil' value")
		elif arg[0] == 'int':
			try:
				arg[1] = int(arg[1])
			except (ValueError, TypeError, OverflowError):
				raise ParseError("invalid 'int' value: '%s'" % arg[1])
		elif arg[0] == 'float':
			try:
				arg[1] = float.fromhex(arg[1])
			except (ValueError, TypeError):
				raise ParseError("invalid 'float' value: '%s'" % arg[1])
		elif arg[0] == 'bool':
			if arg[1] != 'true' and arg[1] != 'false':
				raise ParseError("invalid 'bool' value: '%s'" % arg[1])
		elif arg[0] == 'string':
			if arg[1] == None:
				arg[1] = ''
			elif ('#' in arg[1] or re.search(r"\s", arg[1])):
				raise ParseError("invalid 'string' value: '%s'" % arg[1])
			else:
				for i in range(0,len(arg[1])):
					if i == len(arg[1]):
						break;
					if arg[1][i] == '\\':
						try:
							escape = arg[1][i+1] + arg[1][i+2] + arg[1][i+3]
							escape = int(escape)
							arg[1] = arg[1][:i] + chr(escape) + arg[1][i+4:]
						except (ValueError, TypeError, IndexError):
							raise ParseError("invalid 'string' value: '%s'" % arg[1])
		else:
			raise ParseError("invalid symbol: cannot be '%s'" % arg[0])

	def checkLabel(self, arg, ind):
		if arg[0] != 'label':
			raise ParseError("type label is needed, not '%s'" % arg[0])
		if not re.match(r"^[a-zá-žA-ZÁ-Ž_\-$&%*?!][\w\-$&%*?!]*$", arg[1]):
			raise ParseError("label '%s' is invalid" % arg[1])
		if ind != -1:	#if == -1 , that means instructions CALL JUMP etc
			if arg[1] in self.labels:
				#case when was already defined but JUMP-like instructions went before that definitions
				# if ind == self.labelIndex[self.labels.index(arg[1])]:
				# 	pass
				# else:
				raise SemanticsError("Redefinition of label '%s'" % arg[1])	
			else:			#this means instruction LABEL
				self.labels.append(arg[1])
				self.labelIndex.append(ind)		#saves index in the whole code, to faster execution
		
	def checkType(self, arg):
		if arg[0] != 'type':
			raise ParseError("arg 'type' is needed, not '%s'" % arg[0])
		if arg[1] not in TYPE:
			raise ParseError("invalid type: '%s'" % arg[1])

	#goes to entered label and returns the index where the label is located in code)
	def goToLabel(self, label, call):
		if label not in self.labels: 
			raise SemanticsError("could not go to label '%s', it is not defined" % label)
		else: 
			if call != -1:
				self.calls.append(call)
			move = self.labelIndex[self.labels.index(label)]
			return move

	def interpret(self, inputFile, inputBool):
		current = 0
		while current < len(self.instructions):
			self.instrCount += 1
			if self.instructions[current][0].upper() == "MOVE":
				self.run.move(self.instructions[current][1][0][1].split('@',1),
							self.instructions[current][1][1])
			elif self.instructions[current][0].upper() == "CREATEFRAME":
				self.run.TF = []
			elif self.instructions[current][0].upper() == "PUSHFRAME":
				self.run.pushFrame()
			elif self.instructions[current][0].upper() == "POPFRAME":
				self.run.popFrame()
			elif self.instructions[current][0].upper() == "DEFVAR":
				self.run.defVar(self.instructions[current][1][0][1].split('@',1))
			elif self.instructions[current][0].upper() == "CALL":
				current = self.goToLabel(self.instructions[current][1][0][1], current)
				self.instrCount += 1
			elif self.instructions[current][0].upper() == "RETURN":
				if self.calls == []:
					raise MissingValue("empty CALL stack")
				else:
					current = self.calls.pop(-1)
			elif self.instructions[current][0].upper() == "PUSHS":
				self.run.pushs(self.instructions[current][1][0])
			elif self.instructions[current][0].upper() == "POPS":
				self.run.pops(self.instructions[current][1][0][1].split('@',1))
			elif self.instructions[current][0].upper() == "ADD":
				self.run.calculate("ADD",self.instructions[current][1][0][1].split('@',1),
										self.instructions[current][1][1],
										self.instructions[current][1][2])
			elif self.instructions[current][0].upper() == "SUB":
				self.run.calculate("SUB",self.instructions[current][1][0][1].split('@',1),
										self.instructions[current][1][1],
										self.instructions[current][1][2])
			elif self.instructions[current][0].upper() == "MUL":
				self.run.calculate("MUL",self.instructions[current][1][0][1].split('@',1),
										self.instructions[current][1][1],
										self.instructions[current][1][2])
			elif self.instructions[current][0].upper() == "IDIV":
				self.run.calculate("IDIV",self.instructions[current][1][0][1].split('@',1),
										self.instructions[current][1][1],
										self.instructions[current][1][2])
			elif self.instructions[current][0].upper() == "DIV":
				self.run.calculate("DIV",self.instructions[current][1][0][1].split('@',1),
										self.instructions[current][1][1],
										self.instructions[current][1][2])
			elif self.instructions[current][0].upper() == "LT":
				self.run.conditions("LT",self.instructions[current][1][0][1].split('@',1),
										self.instructions[current][1][1],
										self.instructions[current][1][2])
			elif self.instructions[current][0].upper() == "GT":
				self.run.conditions("GT",self.instructions[current][1][0][1].split('@',1),
										self.instructions[current][1][1],
										self.instructions[current][1][2])
			elif self.instructions[current][0].upper() == "EQ":
				self.run.conditions("EQ",self.instructions[current][1][0][1].split('@',1),
										self.instructions[current][1][1],
										self.instructions[current][1][2])
			elif self.instructions[current][0].upper() == "AND":
				self.run.logical("AND",self.instructions[current][1][0][1].split('@',1),
										self.instructions[current][1][1],
										self.instructions[current][1][2])
			elif self.instructions[current][0].upper() == "OR":
				self.run.logical("OR",self.instructions[current][1][0][1].split('@',1),
										self.instructions[current][1][1],
										self.instructions[current][1][2])
			elif self.instructions[current][0].upper() == "NOT":
				self.run.logical("NOT",self.instructions[current][1][0][1].split('@',1),
										self.instructions[current][1][1])
			elif self.instructions[current][0].upper() == "INT2CHAR":
				self.run.int2Char(self.instructions[current][1][0][1].split('@',1),
										self.instructions[current][1][1])
			elif self.instructions[current][0].upper() == "FLOAT2INT":
				self.run.float2Int(self.instructions[current][1][0][1].split('@',1),
										self.instructions[current][1][1])
			elif self.instructions[current][0].upper() == "INT2FLOAT":
				self.run.int2Float(self.instructions[current][1][0][1].split('@',1),
										self.instructions[current][1][1])
			elif self.instructions[current][0].upper() == "STRI2INT":
				self.run.stri2Int(self.instructions[current][1][0][1].split('@',1),
										self.instructions[current][1][1],
										self.instructions[current][1][2])
			elif self.instructions[current][0].upper() == "READ":
				self.run.read(self.instructions[current][1][0][1].split('@',1),
							self.instructions[current][1][1][1], inputFile, inputBool)
			elif self.instructions[current][0].upper() == "WRITE":
				self.run.write(self.instructions[current][1][0])
			elif self.instructions[current][0].upper() == "CONCAT":
				self.run.concat(self.instructions[current][1][0][1].split('@',1),
								self.instructions[current][1][1],
								self.instructions[current][1][2])
			elif self.instructions[current][0].upper() == "STRLEN":
				self.run.strlen(self.instructions[current][1][0][1].split('@',1),
								self.instructions[current][1][1])
			elif self.instructions[current][0].upper() == "GETCHAR":
				self.run.getchar(self.instructions[current][1][0][1].split('@',1),
								self.instructions[current][1][1],
								self.instructions[current][1][2])
			elif self.instructions[current][0].upper() == "SETCHAR":
				self.run.setchar(self.instructions[current][1][0][1].split('@',1),
								self.instructions[current][1][1],
								self.instructions[current][1][2])
			elif self.instructions[current][0].upper() == "TYPE":
				self.run.instrType(self.instructions[current][1][0][1].split('@',1),
								self.instructions[current][1][1])
			elif self.instructions[current][0].upper() == "LABEL":
				pass #did it earlier
			elif self.instructions[current][0].upper() == "JUMP":
				current = self.goToLabel(self.instructions[current][1][0][1], -1)
				self.instrCount += 1
			elif self.instructions[current][0].upper() == "JUMPIFEQ":
				retBool = self.run.condJumps("JUMPIFEQ", self.instructions[current][1][1],
								self.instructions[current][1][2])
				if retBool == True:
					current = self.goToLabel(self.instructions[current][1][0][1], -1)
					self.instrCount += 1
			elif self.instructions[current][0].upper() == "JUMPIFNEQ":
				retBool = self.run.condJumps("JUMPIFNEQ", self.instructions[current][1][1],
								self.instructions[current][1][2])
				if retBool == True:
					current = self.goToLabel(self.instructions[current][1][0][1], -1)
					self.instrCount += 1
			elif self.instructions[current][0].upper() == "EXIT":
				self.run.instrExit(self.instructions[current][1][0])
			elif self.instructions[current][0].upper() == "DPRINT":
				self.run.dprint(self.instructions[current][1][0])
			elif self.instructions[current][0].upper() == "BREAK":
				justToBeExact = 'th'
				if current == 1:
					justToBeExact = 'st'
				elif current == 2:
					justToBeExact = 'nd'
				elif current == 3:
					justToBeExact = 'rd'
				sys.stderr.write(
"""Currently providing instruction:				{0}{6} instruction (out of {7})
Count of executed instructions were (this one excluded): 	{1}
Currently in data stack:	{2}
Currently in Global Frame:	{3}
Currently in Temporary Frame:	{4}
Currently in Local Frame:	{5}
""".format(current +1,self.instrCount -1, self.run.dataStack, self.run.GF, 
	self.run.TF, self.run.LF,justToBeExact,len(self.instructions)))
			elif xmlInstr[ind][0].upper() == "CLEARS":
				self.run.dataStack = []
			elif xmlInstr[ind][0].upper() == "ADDS":
				self.run.calculate("ADDS",None,None,None,True)
			elif xmlInstr[ind][0].upper() == "SUBS":
				self.run.calculate("SUBS",None,None,None,True)
			elif xmlInstr[ind][0].upper() == "MULS":
				self.run.calculate("MULS",None,None,None,True)
			elif xmlInstr[ind][0].upper() == "DIVS":
				self.run.calculate("DIVS",None,None,None,True)
			elif xmlInstr[ind][0].upper() == "IDIVS":
				self.run.calculate("IDIVS",None,None,None,True)
			elif xmlInstr[ind][0].upper() == "LTS":
				self.run.conditions("LT",None,None,None,True)
			elif xmlInstr[ind][0].upper() == "GTS":
				self.run.conditions("GT",None,None,None,True)
			elif xmlInstr[ind][0].upper() == "EQS":
				self.run.conditions("EQ",None,None,None,True)
			elif xmlInstr[ind][0].upper() == "ANDS":
				self.run.logical("ANDS",None,None,None,True)
			elif xmlInstr[ind][0].upper() == "ORS":
				self.run.logical("ORS",None,None,None,True)
			elif xmlInstr[ind][0].upper() == "NOTS":
				self.run.logical("NOTS",None,None,None,True)
			elif xmlInstr[ind][0].upper() == "INT2CHARS":
				self.int2Char(None, None, True)
			elif xmlInstr[ind][0].upper() == "STRI2INTS":
				self.stri2Int(None, None, None, True)
			elif xmlInstr[ind][0].upper() == "INT2FLOATS":
				self.int2Float(None, None, True)
			elif xmlInstr[ind][0].upper() == "FLOAT2INTS":
				self.float2Int(None, None, True)
			elif xmlInstr[ind][0].upper() == "JUMPIFEQS":
				retBool = self.run.condJumps("JUMPIFEQ", None, None, True)
				if retBool == True:
					current = self.goToLabel(self.instructions[current][1][0][1], -1)
					self.instrCount += 1
			elif xmlInstr[ind][0].upper() == "JUMPIFNEQS":
				retBool = self.run.condJumps("JUMPIFNEQ", None, None, True)
				if retBool == True:
					current = self.goToLabel(self.instructions[current][1][0][1], -1)
					self.instrCount += 1
			current += 1
		self.initVars = self.run.initializedVars

'''
Classes for managing error cases with the error message
'''
class ParseError(Exception):
	pass
class SemanticsError(Exception):
	pass
class WrongArgTypes(Exception):
	pass
class UndefinedVar(Exception):
	pass
class FrameError(Exception):
	pass
class MissingValue(Exception):
	pass
class WrongValue(Exception):
	pass
class StringError(Exception):
	pass


		
			

