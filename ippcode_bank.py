import re
import xml.etree.ElementTree as elemTree


TYPE = ['int', 'bool', 'string', 'nil']

ARG_TYPE = ["int", "bool", "string", "label", "var"]

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

class Interpret:
	def __init__(self):
		self.instructions = []
		self.labels = []
		self.calls = []

	def checkArgCount(self, instr, countGiven, actualCount):
		#you know what to do here
		pass

	def checkInstr(self, order, xmlInstr):

		for i in range(0,len(xmlInstr)):
			if xmlInstr[i][0].upper() not in INSTRUCTIONS:
				raise ParseError("'%s' instruction does not exist" % xmlInstr[i][0])
			try:
				if xmlInstr[i][0].upper() == "MOVE":
					self.checkArgCount(xmlInstr[i][0], len(xmlInstr[i]) - 1, 2)
					# self.var(xmlInstr[i][1])
					# self.symb(xmlInstr[i][2])
				elif xmlInstr[i][0].upper() == "CREATEFRAME":
					self.checkArgCount(xmlInstr[i][0] ,len(xmlInstr[i]) -1, 0)
				elif xmlInstr[i][0].upper() == "PUSHFRAME":
					self.checkArgCount(xmlInstr[i][0] ,len(xmlInstr[i]) -1, 0)
				elif xmlInstr[i][0].upper() == "POPFRAME":
					self.checkArgCount(xmlInstr[i][0] ,len(xmlInstr[i]) -1, 0)
				elif xmlInstr[i][0].upper() == "DEFVAR":
					self.checkArgCount(xmlInstr[i][0] ,len(xmlInstr[i]) -1, 1)
					# self.var(xmlInstr[0])
				elif xmlInstr[i][0].upper() == "CALL":
					self.checkArgCount(xmlInstr[i][0] ,len(xmlInstr[i]) -1, 1)
					# self.label(xmlInstr[0])
				elif xmlInstr[i][0].upper() == "RETURN":
					self.checkArgCount(xmlInstr[i][0] ,len(xmlInstr[i]) -1, 0)
				elif xmlInstr[i][0].upper() == "PUSHS":
					self.checkArgCount(xmlInstr[i][0] ,len(xmlInstr[i]) -1, 1)
					# self.symb(xmlInstr[0])
				elif xmlInstr[i][0].upper() == "POPS":
					self.checkArgCount(xmlInstr[i][0] ,len(xmlInstr[i]) -1, 1)
					# self.var(xmlInstr[0])
				elif xmlInstr[i][0].upper() == "ADD":
					self.checkArgCount(xmlInstr[i][0] ,len(xmlInstr[i]) -1, 3)
					# self.var(xmlInstr[0])
					# self.symb(xmlInstr[1])
					# self.symb(xmlInstr[2])
				elif xmlInstr[i][0].upper() == "SUB":
					self.checkArgCount(xmlInstr[i][0] ,len(xmlInstr[i]) -1, 3)
					# self.var(xmlInstr[0])
					# self.symb(xmlInstr[1])
					# self.symb(xmlInstr[2])
				elif xmlInstr[i][0].upper() == "MUL":
					self.checkArgCount(xmlInstr[i][0] ,len(xmlInstr[i]) -1, 3)
					# self.var(xmlInstr[0])
					# self.symb(xmlInstr[1])
					# self.symb(xmlInstr[2])
				elif xmlInstr[i][0].upper() == "IDIV":
					self.checkArgCount(xmlInstr[i][0] ,len(xmlInstr[i]) -1, 3)
					# self.var(xmlInstr[0])
					# self.symb(xmlInstr[1])
					# self.symb(xmlInstr[2])
				elif xmlInstr[i][0].upper() == "DIV":
					self.checkArgCount(xmlInstr[i][0] ,len(xmlInstr[i]) -1, 3)
					# self.var(xmlInstr[0])
					# self.symb(xmlInstr[1])
					# self.symb(xmlInstr[2])
				elif xmlInstr[i][0].upper() == "LT":
					self.checkArgCount(xmlInstr[i][0] ,len(xmlInstr[i]) -1, 3)
					# self.var(xmlInstr[0])
					# self.symb(xmlInstr[1])
					# self.symb(xmlInstr[2])
				elif xmlInstr[i][0].upper() == "GT":
					self.checkArgCount(xmlInstr[i][0] ,len(xmlInstr[i]) -1, 3)
					# self.var(xmlInstr[0])
					# self.symb(xmlInstr[1])
					# self.symb(xmlInstr[2])
				elif xmlInstr[i][0].upper() == "EQ":
					self.checkArgCount(xmlInstr[i][0] ,len(xmlInstr[i]) -1, 3)
					# self.var(xmlInstr[0])
					# self.symb(xmlInstr[1])
					# self.symb(xmlInstr[2])
				elif xmlInstr[i][0].upper() == "AND":
					self.checkArgCount(xmlInstr[i][0] ,len(xmlInstr[i]) -1, 3)
					# self.var(xmlInstr[0])
					# self.symb(xmlInstr[1])
					# self.symb(xmlInstr[2])
				elif xmlInstr[i][0].upper() == "OR":
					self.checkArgCount(xmlInstr[i][0] ,len(xmlInstr[i]) -1, 3)
					# self.var(xmlInstr[0])
					# self.symb(xmlInstr[1])
					# self.symb(xmlInstr[2])
				elif xmlInstr[i][0].upper() == "NOT":
					self.checkArgCount(xmlInstr[i][0] ,len(xmlInstr[i]) -1, 2)
					# self.var(xmlInstr[0])
					# self.symb(xmlInstr[1])
				elif xmlInstr[i][0].upper() == "INT2CHAR":
					self.checkArgCount(xmlInstr[i][0] ,len(xmlInstr[i]) -1, 2)
					# self.var(xmlInstr[0])
					# self.symb(xmlInstr[1])
				elif xmlInstr[i][0].upper() == "STRI2INT":
					self.checkArgCount(xmlInstr[i][0] ,len(xmlInstr[i]) -1, 3)
					# self.var(xmlInstr[0])
					# self.symb(xmlInstr[1])
					# self.symb(xmlInstr[2])
				elif xmlInstr[i][0].upper() == "READ":
					self.checkArgCount(xmlInstr[i][0] ,len(xmlInstr[i]) -1, 2)
					# self.var(xmlInstr[0])
					# self.type(xmlInstr[1])
				elif xmlInstr[i][0].upper() == "WRITE":
					self.checkArgCount(xmlInstr[i][0] ,len(xmlInstr[i]) -1, 1)
					# self.symb(xmlInstr[0])
				elif xmlInstr[i][0].upper() == "CONCAT":
					self.checkArgCount(xmlInstr[i][0] ,len(xmlInstr[i]) -1, 3)
					# self.var(xmlInstr[0])
					# self.symb(xmlInstr[1])
					# self.symb(xmlInstr[2])
				elif xmlInstr[i][0].upper() == "STRLEN":
					self.checkArgCount(xmlInstr[i][0] ,len(xmlInstr[i]) -1, 2)
					# self.var(xmlInstr[0])
					# self.symb(xmlInstr[1])
				elif xmlInstr[i][0].upper() == "GETCHAR":
					self.checkArgCount(xmlInstr[i][0] ,len(xmlInstr[i]) -1, 3)
					# self.var(xmlInstr[0])
					# self.symb(xmlInstr[1])
					# self.symb(xmlInstr[2])
				elif xmlInstr[i][0].upper() == "SETCHAR":
					self.checkArgCount(xmlInstr[i][0] ,len(xmlInstr[i]) -1, 3)
					# self.var(xmlInstr[0])
					# self.symb(xmlInstr[1])
					# self.symb(xmlInstr[2])
				elif xmlInstr[i][0].upper() == "TYPE":
					self.checkArgCount(xmlInstr[i][0] ,len(xmlInstr[i]) -1, 2)
					# self.var(xmlInstr[0])
					# self.symb(xmlInstr[1])
				elif xmlInstr[i][0].upper() == "LABEL":
					self.checkArgCount(xmlInstr[i][0] ,len(xmlInstr[i]) -1, 1)
					# self.label(xmlInstr[0])
					# self.add_label(xmlInstr[0], position)
				elif xmlInstr[i][0].upper() == "JUMP":
					self.checkArgCount(xmlInstr[i][0] ,len(xmlInstr[i]) -1, 1)
					# self.label(xmlInstr[0])
				elif xmlInstr[i][0].upper() == "JUMPIFEQ":
					self.checkArgCount(xmlInstr[i][0] ,len(xmlInstr[i]) -1, 3)
					# self.label(xmlInstr[0])
					# self.symb(xmlInstr[1])
					# self.symb(xmlInstr[2])
				elif xmlInstr[i][0].upper() == "JUMPIFNEQ":
					self.checkArgCount(xmlInstr[i][0] ,len(xmlInstr[i]) -1, 3)
					# self.label(xmlInstr[0])
					# self.symb(xmlInstr[1])
					# self.symb(xmlInstr[2])
				elif xmlInstr[i][0].upper() == "EXIT":
					self.checkArgCount(xmlInstr[i][0] ,len(xmlInstr[i]) -1, 1)
					# self.symb(xmlInstr[0])
				elif xmlInstr[i][0].upper() == "DPRINT":
					self.checkArgCount(xmlInstr[i][0] ,len(xmlInstr[i]) -1, 1)
					# self.symb(xmlInstr[0])
				elif xmlInstr[i][0].upper() == "BREAK":
					self.checkArgCount(xmlInstr[i][0] ,len(xmlInstr[i]) -1, 0)
			except IndexError:
				raise ParseError("wrong arguments for instruction '%s'" % xmlInstr[i][0])

		
		
