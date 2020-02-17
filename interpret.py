import xml.etree.ElementTree as elemTree
import argparse as argumentParser
import sys

#aby sa predoslo pouzivaniu vstavanej chybovej hlasky z argparse
class ArgumentParser(argumentParser.ArgumentParser):	
	def error(self, message):
		sys.stderr.write("Chyba: Použité nesprávne argumenty!\n")
		exit(10)

# pridanie ostatných prípustných argumentov
parser = ArgumentParser(add_help=False)
parser.add_argument("--help", action="store_true")
parser.add_argument("--source",action="store_true")
parser.add_argument("--stats",action="store_true")
parser.add_argument("--insts", action="store_true")
parser.add_argument("--vars", action="store_true")

arguments = parser.parse_args()

if arguments.help:
	if len(sys.argv) != 2:
		sys.stderr.write("CHYBA: argument '--help' je potrebné použiť samostatne!\n")
		exit(10)
	else:
		print("POMOC SO SKRIPTOM")
		exit(0)

for x in range(1,len(sys.argv)):
	if not arguments.source or not arguments.stats:
		sys.stderr.write("CHYBA, nie je zadaný parameter '--source' alebo '--stats'!\n")
		exit(10)

	if (sys.argv[x] == '--insts'):
		print('--insts accepted')	#vypise sa do suboru
	elif (sys.argv[x] == '--vars'):
		print('--vars accepted')	#vypise sa do suboru


