import xml.etree.ElementTree as elemTree
import argparse as argumentParser
import sys
import os
import ippcode_bank 


"""
	ARGS PARSING SECTION
"""
#to override built in error message from argparse
class ArgumentParser(argumentParser.ArgumentParser):	
	def error(self, message):
		sys.stderr.write("ERROR: Used wrong arguments! Use '--help' for program manual.\n")
		sys.exit(10)

# adding possible options 
parser = ArgumentParser(add_help=False)
parser.add_argument("--help", action="store_true")
parser.add_argument("--source", metavar="FILE", type=str)
parser.add_argument("--input",  metavar="FILE", type=str)
parser.add_argument("--stats",action="store_true")			#metavar='FILE'	type=str
parser.add_argument("--insts", action="store_true")
parser.add_argument("--vars", action="store_true")

arguments = parser.parse_args()

if arguments.help:
	if len(sys.argv) != 2:
		sys.stderr.write("ERROR: '--help' need to be used standalone.\n") 
		exit(10)
	else:
		print("POMOC SO SKRIPTOM takze tu treba este dopisat stracky na pomoc")
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
	arguments.input = sys.stdin

if (arguments.insts or arguments.vars) and not arguments.stats:
	sys.stderr.write("ERORR: '--insts' or '--vars' used without '--stats'!\n")
	exit(10)

#TOTO SA BUDE MUSIET ASI PRIDAT NAKONIEC
for x in range(1,len(sys.argv)):
	if (sys.argv[x] == '--insts'):
		print('--insts accepted')	#prints to file
	elif (sys.argv[x] == '--vars'):
		print('--vars accepted')	#prints to file
"""
END OF ARGS PARSING SECTION
"""

#kontrolovat spravnost XML

class XMLparser:
	def checkXML(source):
		tree = elemTree.parse(source)
		# Valid root element
		root = tree.getroot()
		if root.tag != "program":
			raise elemTree.ParseError("root element must be 'program' not: '%s'" % root.tag)

		if "language" not in root.attrib:
			raise elemTree.ParseError("missing attribute 'language'")

		for attrib, value in root.attrib.items():
			if attrib == "language":
				if value.upper() != "IPPCODE20":
					raise elemTree.ParseError("language must be 'IPPcode20'")
			elif attrib != "name" and attrib != "description":
				raise elemTree.ParseError("program element can only contain language, name or description attributes")	
		return root			

	def checkBody(source):
		instrList = []
		checkArgCount = ['1', '2', '3']
		checkType = ["int", "bool", "string", "label", "var", "type"]
		for instr in source:
			if (instr.tag != "instruction"):
				raise elemTree.ParseError("can only contain 'instruction' subelements not: '%s'" % instr.tag)
			if (instr.get('order') == None or instr.get('opcode') == None):
				raise elemTree.ParseError("instruction needs 'order' and 'opcode'")
			instruction = []
			instruction.append(instr.get('opcode'))
			checkInt = 0
			for deepchild in instr:
				checkInt += 1
				if (deepchild.tag[:3] != "arg"):
					raise elemTree.ParseError("wrong arguments in XML: '%s'" % deepchild.tag)
				if (deepchild.tag[3:] not in checkArgCount or (checkInt != int(deepchild.tag[3:]))):
					raise elemTree.ParseError("wrong arguments count in instruction: '%s'" % deepchild.tag[3:])
				if (deepchild.get('type') == None):
					raise elemTree.ParseError("argument needs to have 'type' defined")
				if (deepchild.get('type') not in checkType):
					raise elemTree.ParseError("undefined type: '%s'" % deepchild.get('type'))
				args = [deepchild.get('type'), deepchild.text]
				instruction.append(args)
				# print (deepchild.get('type'), deepchild.text.split('@',1))	#first occurence
			instrList.append(instruction)

		orderList = []
		for i in range(0,len(source)):
			try:
				if int(source[i].get('order')) in orderList:
					raise elemTree.ParseError("at least 2 same order types: '%s' exists many times" % source[i].get('order'))
				orderList.append(int(source[i].get('order')))
			except ValueError:
				raise elemTree.ParseError("wrong 'order' type: '%s'" % source[i].get('order'))
	
		orderList = sorted(enumerate(orderList), key=lambda x: x[1])
		return orderList, instrList


try:
	xmlRoot = XMLparser.checkXML(arguments.source)	#checkXMLhead
	orderList, instrList= XMLparser.checkBody(xmlRoot)		#check the rest of XML
	program = ippcode_bank.Interpret()
	program.checkInstr(orderList, instrList) 
	

except elemTree.ParseError as wrongxml:
	sys.stderr.write("ERROR: wrong XML format-> %s!\n" % str(wrongxml))
	exit(31)
except FileNotFoundError:
    sys.stderr.write("ERROR: Source file cannot be opened !\n")
    exit(11)
except ippcode_bank.ParseError as wrongsyntax:
	sys.stderr.write("ERROR: syntax error-> %s!\n" % str(wrongsyntax))
	exit(32)
