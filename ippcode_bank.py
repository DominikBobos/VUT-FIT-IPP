import re
import xml.etree.ElementTree as elemTree
import ippcode_dependencies

TYPE = ['int', 'bool', 'string', 'nil']

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
				"INT2CHAR", "STRI2INT", 
				"READ", "WRITE", 
				"CONCAT", "STRLEN", 
				"GETCHAR", "SETCHAR", 
				"TYPE", 
				"LABEL", 
				"JUMP", "JUMPIFEQ", "JUMPIFNEQ",
				"EXIT", 
				"DPRINT", 
				"BREAK" ]


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

class Interpret:
	def __init__(self):
		self.instructions = []
		self.labels = []
		self.calls = []
		self.labelIndex = []		#saves index of LABEL opcode in the correct order, so it saves time
		self.run = ippcode_dependencies.Frames()

	def checkArgCount(self, instr, countGiven, neededCount):
		if countGiven == neededCount:
			pass
		else:
			raise ParseError("wrong number of arguments '{0}' needs '{1}' not '{2}' args".format(instr, neededCount, countGiven))

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
					self.checkLabel(xmlInstr[ind][1], False)
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
					self.checkLabel(xmlInstr[ind][1], ind)
				elif xmlInstr[ind][0].upper() == "JUMP":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 1)
					self.checkLabel(xmlInstr[ind][1], False)
				elif xmlInstr[ind][0].upper() == "JUMPIFEQ":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 3)
					self.checkLabel(xmlInstr[ind][1], False)
					self.checkSymb(xmlInstr[ind][2])
					self.checkSymb(xmlInstr[ind][3])
				elif xmlInstr[ind][0].upper() == "JUMPIFNEQ":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 3)
					self.checkLabel(xmlInstr[ind][1], False)
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
				temp = [xmlInstr[order[i][0]][0], xmlInstr[order[i][0]][1:]]
				#vlozenie instrukcii s argumentami v poradi ako sa budu vykonavat
				self.instructions.append(temp)
				#self.instructions.append({"instruction": xmlInstr[order[i][0]][0], "args": xmlInstr[order[i][0]][1:]})

			except IndexError:
				raise ParseError("wrong arguments for instruction '%s'" % xmlInstr[ind][0])
		
		# princip vyhladavania napr labels, na jumpy etc
		#najskor najde odpovedajucu instrukciu
		# vpripade uspechu hlada danu vec v danej instrukcii 
		# v pripade uspechu to tu vyprintuje
		
		# print(self.labelIndex, self.labels)				
		#print(self.instructions[self.labelIndex[0]][1][0][1])
		# print(self.instructions)
		for item in self.instructions:
			if "DEFVAR" in item:
				for found in item[1]:
					if "GF@space" in found:
						print(found[1])
		self.interpret()

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
			except (ValueError, TypeError):
				raise ParseError("invalid 'int' value: '%s'" % arg[1])
		elif arg[0] == 'bool':
			if arg[1] != 'true' and arg[1] != 'false':
				raise ParseError("invalid 'bool' value: '%s'" % arg[1])
		elif arg[0] == 'string':
			if arg[1] == None:
				arg[1] == ''
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
		
		if ind != False:
			if arg[1] in self.labels:
				sys.stderr.write("Redefinition of label '%s'!\n" % arg[1])
				exit(52)
			else:
				self.labels.append(arg[1])
				self.labelIndex.append(ind)

	def checkType(self, arg):
		if arg[0] != 'type':
			raise ParseError("arg 'type' is needed, not '%s'" % arg[0])
		if arg[1] not in TYPE:
			raise ParseError("invalid type: '%s'" % arg[1])

	def interpret(self):
		current = 0
		while current < len(self.instructions):
			if self.instructions[current][0].upper() == "MOVE":
				pass
			elif self.instructions[current][0].upper() == "CREATEFRAME":
				self.run.tempFrame = []
			elif self.instructions[current][0].upper() == "PUSHFRAME":
				self.run.pushFrame()
			elif self.instructions[current][0].upper() == "POPFRAME":
				self.run.popFrame()
			elif self.instructions[current][0].upper() == "DEFVAR":
				pass
			elif self.instructions[current][0].upper() == "CALL":
				pass
				pass
			elif self.instructions[current][0].upper() == "RETURN":
				pass
			elif self.instructions[current][0].upper() == "PUSHS":
				pass
				pass
			elif self.instructions[current][0].upper() == "POPS":
				pass
				pass
			elif self.instructions[current][0].upper() == "ADD":
				pass
				pass
				pass
				pass
			elif self.instructions[current][0].upper() == "SUB":
				pass
				pass
				pass
				pass
			elif self.instructions[current][0].upper() == "MUL":
				pass
				pass
				pass
				pass
			elif self.instructions[current][0].upper() == "IDIV":
				pass
				pass
				pass
				pass
			elif self.instructions[current][0].upper() == "DIV":
				pass
				pass
				pass
				pass
			elif self.instructions[current][0].upper() == "LT":
				pass
				pass
				pass
				pass
			elif self.instructions[current][0].upper() == "GT":
				pass
				pass
				pass
				pass
			elif self.instructions[current][0].upper() == "EQ":
				pass
				pass
				pass
				pass
			elif self.instructions[current][0].upper() == "AND":
				pass
				pass
				pass
				pass
			elif self.instructions[current][0].upper() == "OR":
				pass
				pass
				pass
				pass
			elif self.instructions[current][0].upper() == "NOT":
				pass
				pass
				pass
			elif self.instructions[current][0].upper() == "INT2CHAR":
				pass
				pass
				pass
			elif self.instructions[current][0].upper() == "STRI2INT":
				pass
				pass
				pass
				pass
			elif self.instructions[current][0].upper() == "READ":
				pass
				pass
				pass
			elif self.instructions[current][0].upper() == "WRITE":
				pass
				pass
			elif self.instructions[current][0].upper() == "CONCAT":
				pass
				pass
				pass
				pass
			elif self.instructions[current][0].upper() == "STRLEN":
				pass
				pass
				pass
			elif self.instructions[current][0].upper() == "GETCHAR":
				pass
				pass
				pass
				pass
			elif self.instructions[current][0].upper() == "SETCHAR":
				pass
				pass
				pass
				pass
			elif self.instructions[current][0].upper() == "TYPE":
				pass
				pass
				pass
			elif self.instructions[current][0].upper() == "LABEL":
				pass
				pass
			elif self.instructions[current][0].upper() == "JUMP":
				pass
				pass
			elif self.instructions[current][0].upper() == "JUMPIFEQ":
				pass
				pass
				pass
				pass
			elif self.instructions[current][0].upper() == "JUMPIFNEQ":
				pass
				pass
				pass
				pass
			elif self.instructions[current][0].upper() == "EXIT":
				pass
				pass
			elif self.instructions[current][0].upper() == "DPRINT":
				pass
				pass
			elif self.instructions[current][0].upper() == "BREAK":
				pass

			current += 1


		
			

