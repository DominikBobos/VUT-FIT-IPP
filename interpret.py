import xml.etree.ElementTree as elemTree
import argparse as argumentParser
import sys
import os
import ippcode_bank 



#Class just to override built in error message from argparse
class ArgumentParser(argumentParser.ArgumentParser):	
	def error(self, message):
		sys.stderr.write("ERROR: Used wrong arguments! Use '--help' for program manual.\n")
		sys.exit(10)

"""
	INPUT SYS.ARGS PARSING SECTION
"""
# adding possible options 
parser = ArgumentParser(add_help=False)
parser.add_argument("--help", action="store_true")
parser.add_argument("--source", metavar="FILE", type=str)
parser.add_argument("--input",  metavar="FILE", type=str)
parser.add_argument("--stats", metavar="FILE", type=str)
parser.add_argument("--insts", action="store_true")
parser.add_argument("--vars", action="store_true")

arguments = parser.parse_args()
inputBool = True
if arguments.help:
	if len(sys.argv) != 2:
		sys.stderr.write("ERROR: '--help' need to be used standalone.\n") 
		exit(10)
	else:
		print(
"""#####PROGRAM interpret.py USAGE#####
### This program loads XMLfile and executes instructions written in IPPcode20 ###
* --source=FILE -> this argument stores XMLfile with IPPcode20 (when not stated, it loads from STDIN)
* --input=FILE -> this argument stores data that IPPcode20 needs (when not stated, it loads from STDIN)
* --stats=FILE -> this argument will contain statistics data about the executed XML file
** --insts -> extension for --stats, stats about all executed instructions
** --vars -> extension for --stats, stats about all initialized variables""")
		exit(0)

if not arguments.source and not arguments.input:
	sys.stderr.write("ERROR: use at least one argument '--source' or '--input'!\n")
	exit(10)
else:
	if arguments.source and not os.path.isfile(arguments.source):
		sys.stderr.write("ERROR: Cannot open input file set by --source.\n")
		exit(11)
	if arguments.input and not os.path.isfile(arguments.input):
		sys.stderr.write("ERROR: Cannot open input file set by --input.\n")
		exit(11)

if not arguments.source:
	arguments.source = sys.stdin
if not arguments.input:
	inputBool = False
	arguments.input = sys.stdin

if (arguments.insts or arguments.vars) and not arguments.stats:
	sys.stderr.write("ERORR: '--insts' or '--vars' used without '--stats'!\n")
	exit(10)
"""
	END OF ARGS PARSING SECTION
"""


"""
	Class for parsing XMLfile with IPPcode20 language
	Checks well-formness
	Checks syntax and lexical errors 
"""
class XMLparser:
	"""Gets XMLelements_tree using xml.etree.ElementTree library
	source is XMLfile, it checks the IPPcode20 header if false it returns 31"""
	def checkXML(source):
		tree = elemTree.parse(source)
		# Valid root element
		root = tree.getroot()
		#checking if XML has the right IPPcode20 header
		if root.tag != "program":
			raise ippcode_bank.ParseError("root element must be 'program' not: '%s'" % root.tag)

		if "language" not in root.attrib:
			raise ippcode_bank.ParseError("missing attribute 'language'")

		for attrib, value in root.attrib.items():
			if attrib == "language":
				if value.upper() != "IPPCODE20":
					raise ippcode_bank.ParseError("language must be 'IPPcode20'")
			elif attrib != "name" and attrib != "description":
				raise ("program element can only contain language, name or description attributes")	
		return root			
	"""Source is the XMLtree with all the attributes
	function checks syntax and lexical errors 
	exception raises when error
	returns the correct order and instructions list"""
	def checkBody(source):
		instrList = []							#holds the correct order of all used instructions
		checkArgCount = ['1', '2', '3']			#the only possible attribute args count	
		checkType = ["int", "bool", "string", "label", "var", "type", "nil", "float"]	#available types
		for instr in source:
			if (instr.tag != "instruction"):
				raise ippcode_bank.ParseError("can only contain 'instruction' subelements not: '%s'" % instr.tag)
			if (instr.get('order') == None or instr.get('opcode') == None):
				raise ippcode_bank.ParseError("instruction needs 'order' and 'opcode'")
			instruction = []
			instruction.append(instr.get('opcode'))
			checkInt = 0
			arg1 = []
			arg2 = []
			arg3 = []
			#checks if there are correctly numbered arguments 
			for deepchild in instr:
				checkInt += 1
				if (deepchild.tag[:3] != "arg"):
					raise ippcode_bank.ParseError("wrong arguments in XML: '%s'" % deepchild.tag)
				if (deepchild.tag[3:] not in checkArgCount):
					raise ippcode_bank.ParseError("wrong arguments in instruction: '{0}'".format(instr.get('opcode')))
				if (deepchild.get('type') == None):
					raise ippcode_bank.ParseError("argument needs to have 'type' defined")
				if (deepchild.get('type') not in checkType):
					raise ippcode_bank.ParseError("undefined type: '%s'" % deepchild.get('type'))
				if int(deepchild.tag[3:]) == 1:
					arg1 = [deepchild.get('type'), deepchild.text]
				elif int(deepchild.tag[3:]) == 2:
					arg2 = [deepchild.get('type'), deepchild.text]
				elif int(deepchild.tag[3:]) == 3:
					arg3 = [deepchild.get('type'), deepchild.text]
			#gives a correct order to arguments
			checkArg = 0
			if arg1 != []:
				checkArg = 1
				instruction.append(arg1)
			if arg2 != []:
				checkArg = 2
				instruction.append(arg2)
			if arg3 != []:
				checkArg = 3
				instruction.append(arg3)
			if checkArg != checkInt:
				raise ippcode_bank.ParseError("wrong arguments count in instruction: '{0}'".format(instr.get('opcode')))
			instrList.append(instruction)	#appends to instrList a list with ['instruction', [its args]]

		#sorts the order and the corresponding instructions's index thanks to the element 'order'
		orderList = []
		for i in range(0,len(source)):
			try:
				if int(source[i].get('order')) in orderList:
					raise ippcode_bank.ParseError("at least 2 same order types: '%s' exists many times" % source[i].get('order'))
				orderList.append(int(source[i].get('order')))
				if int(source[i].get('order')) < 0:	# negative index of order
					raise ippcode_bank.ParseError("negative 'order' type: '%s'" % source[i].get('order'))
			except (ValueError, TypeError):
				raise ippcode_bank.ParseError("wrong 'order' type: '%s'" % source[i].get('order'))
		# orderList is a list where the item is another list where [0] 
		# is the actual index of instruction
		# in the input XML, so it will execute in the right order 
		orderList = sorted(enumerate(orderList), key=lambda x: x[1])
		return orderList, instrList


try:
	xmlRoot = XMLparser.checkXML(arguments.source)		#checkXMLhead
	orderList, instrList= XMLparser.checkBody(xmlRoot)	#check the rest of XML
	program = ippcode_bank.Interpret()
	program.checkInstr(orderList, instrList) 			#checks if the instruction has correct order
	program.interpret(arguments.input, inputBool)		#runs the whole interpret
	
	#STATI extension
	#prints wanted information to file given to sys.arg --stats
	if arguments.stats:
		try:
			finalStats = ""
			for x in range(1,len(sys.argv)):
				if (sys.argv[x] == '--insts'):
					finalStats += str(program.instrCount)
					finalStats += '\n'
				elif (sys.argv[x] == '--vars'):
					finalStats += str(program.initVars)
					finalStats += '\n'
			file = open(arguments.stats, "w")
			file.seek(0)
			file.write(finalStats)
			file.truncate()
		except IOError:
			sys.stderr.write("ERROR: Could not open/create stats file!\n")
			exit(12)


#Error messages handling with the corresponding error code 
except elemTree.ParseError as wrongxml:
	sys.stderr.write("ERROR: wrong XML format-> %s!\n" % str(wrongxml))
	exit(31)
except TypeError as wrongxml:
	sys.stderr.write("ERROR: wrong XML format-> %s!\n" % str(wrongxml))
	exit(31)
except FileNotFoundError:
	sys.stderr.write("ERROR: Source file cannot be opened !\n")
	exit(11)
except ippcode_bank.ParseError as wrongsyntax:
	sys.stderr.write("ERROR: syntax error-> %s!\n" % str(wrongsyntax))
	exit(32)
except ippcode_bank.SemanticsError as wrongsemantics:
	sys.stderr.write("ERROR: semantics error-> %s!\n" % str(wrongsemantics))
	exit(52)
except ippcode_bank.WrongArgTypes as wrongargs:
	sys.stderr.write("ERROR: wrong operands type-> %s!\n" % str(wrongargs))
	exit(53)
except ippcode_bank.UndefinedVar as wrongvar:
	sys.stderr.write("ERROR: variable error-> %s!\n" % str(wrongvar))
	exit(54)
except ippcode_bank.FrameError as frameError:
	sys.stderr.write("ERROR: %s !\n" % str(frameError))
	exit(55)
except ippcode_bank.MissingValue as missingValue:
	sys.stderr.write("ERROR: missing value-> %s!\n" % str(missingValue))
	exit(56)
except ippcode_bank.WrongValue as wrongvalue:
	sys.stderr.write("ERROR: wrong value-> %s!\n" % str(wrongvalue))
	exit(57)
except ippcode_bank.StringError as wrongstring:
	sys.stderr.write("ERROR: error with string-> %s!\n" % str(wrongstring))
	exit(58)
