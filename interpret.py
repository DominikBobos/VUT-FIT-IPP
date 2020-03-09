import xml.etree.ElementTree as elemTree
import argparse as argumentParser
import sys
import os


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

try:
	tree = elemTree.parse(arguments.source)
	# Valid root element
	root = tree.getroot()
	if root.tag != "program":
		raise elemTree.ParseError("root element must be 'program'")

	if "language" not in root.attrib:
		raise elemTree.ParseError("missing attribute 'language'")

	for attrib, value in root.attrib.items():
		if attrib == "language":
			if value != "IPPcode20":
				raise elemTree.ParseError("language must be 'IPPcode20' ")
		elif attrib != "name" and attrib != "description":
			raise elemTree.ParseError("program element can only contain language, name or description attributes")
	print("zbehol som v pohode")

except elemTree.ParseError as wrongxml:
	sys.stderr.write("ERROR: wrong XML format (%s)!\n" % str(wrongxml))
	exit(31)
except FileNotFoundError:
    sys.stderr.write("ERROR: Source file cannot be opened !\n")
    exit(11)


# class XMLparser:
# 	def __init__(self, input_xml, stack): #, frames, flowControl):
# 		self.__instructions = None
# 		self.__stack = stack
# 		#self.__frames = frames
# 		#self.__flowControl = flowControl  # Instruction counter and labelstack

# 				# Start parsing source XML
# 		try:
# 			tree = elemTree.parse(args.source)
# 			# Valid root element
# 			root = tree.getroot()
# 			if root.tag != "program":
# 				raise elemTree.ParseError("root element must be 'program'")

# 			if "language" not in root.attrib:
# 				raise elemTree.ParseError("missing attribute 'language'")

# 			for attrib, value in root.attrib.items():
# 				if attrib == "language":
# 					if value != "IPPcode20":
# 						raise elemTree.ParseError("language must be 'IPPcode20' ")
# 				elif attrib != "name" and attrib != "description":
# 					raise elemTree.ParseError("program element can only contain language, name or description attributes")

# 		except elemTree.ParseError as wrongxml:
# 			sys.stderr.write("ERROR: wrong XML format (%s)!\n" % str(wrongxml))
# 			exit(31)


# class Interpret:
# 	def __init__(self):
# 		# STATI extension
# 		self.__inst = 0
# 		self.__vars = set()

# 		# Interpret vars
# 		self.__instructionList = []
# 		#self._flowControl = FlowControl()   # Contains instruction counter, position stack and labels dict
# 		self._stack = []
# 		#self._frames = Frames()

# 	def start(self):
# 		xml = XMLparser(self.arguments.source, self._stack )	#, self._frames, self._flowControl)
# 		print('dostal som sa sem?')

# XMLparser.__init__(arguments.source, [] )



