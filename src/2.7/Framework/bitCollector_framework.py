## File Name: bitCollector_framework.py
##
## Author(s): Daniel "Albinohat" Mercado
##
## Purpose: This script will act as the framework supporting the other modules
##          written to collect different types of information as well as perform 
##          module-independent tasks.

## Standard imports (Static)
import json, logging, logging.handlers, platform
import os, re, sys, threading, time

## Third-party imports (Static)

## Global Variable Declarations - CONSTANTS - DO NOT CHANGE @ RUNTIME
_framework_version = "bitCollector_framework v0.2.1 Released 2015-03-09"

## Class Declarations

## Class Name: InitializeBCModuleThread - A thread which parses through and executes a command.
##
## Purpose: Spin up a new thread to run a dynamically imported module.
class InitializeBCModuleThread(threading.Thread):
	## Method Name: __init__
	##
	## Purpose: Initializes a new thread and calls the main method of a BitCollector module.
	##
	## Parameters
	## 1. framework_settings - An instance of the FrameworkSettings class containing settings required to start the framework.
	## 2. platform           - An instance of the Platform class containing the platform-independent attributes as well as a platform-dependent object.
	## 3. module_dict        - The name and parameters to pass to the BitCollector module to be initialized.
	def __init__(self, framework_settings, platform_details, module_dict):
		## Initialize the Logger for this class.
		self.logger = logging.getLogger(self.__class__.__name__)
		self.logger.debug("Entering BitCollector.InitializeBCModuleThread.__init__()")

		## Initialize the absolute path to the running script for dynamic linking in the BitCollector modules.
		self.path_to_main = os.path.dirname(os.path.realpath(__file__))

		## Initialize the parent thread object.
		threading.Thread.__init__(self)

		self.framework_settings = framework_settings
		self.platform_details   = platform_details
		self.module_dict        = module_dict

		self.start()

	## run - This method calls the executeCommand method of the specified feature set.
	def run(self):
		## Get the thread ID
		self.thread_id = threading.current_thread()

		try:
			entry_point = getattr(__import__(self.module_dict["name"]), "main")
			self.logger.info("Successfully imported BitCollector module: " + self.module_dict["name"] + ".main")

			## Call the entry_point (main) method of the BitCollector module.
			self.return_code = entry_point(self.thread_id, self.path_to_main, self.framework_settings, self.platform_details, self.module_dict)

		except AttributeError:
			self.logger.warning("Failed to import BitCollector module: " + self.module_dict["name"] + ".main")

		except ImportError:
			self.logger.warning("Failed to import BitCollector module: " + self.module_dict["name"] + ".main")

## Class Name: FrameworkSettings
##
## Purpose: Hold information about the settings required to run the framework.
class FrameworkSettings():
	## Method Name: __init__
	##
	## Purpose: Initialize the settings required to start the framework.
	##
	## Parameters
	## 1. tuple - A 7-part tuple containing runtime settings.
	##    Index 0 - The path to the file to write the logs to.
	##    Index 1 - The format to in which to save the log file (CSV or HTML)
	##    Index 2 - The default log level which may be overridden by individual modules.
	##    Index 3 - A boolean tracking whether or not to log to the log file.
	##    Index 4 - A boolean tracking whether or not to log to STDOUT.
	##    Index 5 - The list of strings containing additional module paths.
	##    Index 6 - The list of module dictionaries containing module-specific settings.
	def __init__(self, tuple):
		## Initialize the Logger for this class.
		## Store the runtime settings so that modules will have access to them.
		self.log_file         = tuple[0]
		self.logging_format   = tuple[1]
		self.logging_level    = tuple[2]
		self.log_to_file      = tuple[3]
		self.log_to_stdout    = tuple[4]
		self.additional_paths = tuple[5]
		self.module_list      = tuple[6]

		## Initialize the absolute path to the logging directory.
		self.abs_log_dir = os.path.dirname(self.log_file)		

		## Call the method to initialize the root logger.
		self.initializeRootLogger()

	## Method Name: initializeRootLogger
	##
	## Purpose: Initialize the root logger as well as the logging formats and logging streams for the log file and STDOUT.
	def initializeRootLogger(self):	
		## Initialize the logging formats to be used by all modules.
		if (self.logging_format == "csv"):
			self.log_file_formatter = logging.Formatter('%(asctime)s,%(module)s.%(name)s.%(funcName)s,%(levelname)s,%(message)s', '%Y-%m-%dT%H:%M:%S')

		elif (self.logging_format == "html"):
			self.log_file_formatter = logging.Formatter("<tr><td>%(asctime)s</td><td>%(module)s.%(name)s.%(funcName)s</td><td>%(levelname)s</td><td>%(message)s</td></tr>", '%Y-%m-%dT%H:%M:%S')

		else:
			print "Startup - bitCollector_framework.FrameworkSettings.initializeRootLogger - WARNING - Unknown logging format: " + self.logging_format + ". Defaulting to CSV."
			self.logging_format  = "csv"
			self.log_file_formatter = logging.Formatter('%(asctime)s,%(module)s.%(name)s.%(funcName)s,%(levelname)s,%(message)s', '%Y-%m-%dT%H:%M:%S')

		self.log_console_formatter  = logging.Formatter('%(asctime)s - %(module)s.%(name)s.%(funcName)s - [%(levelname)s] - %(message)s', '%Y-%m-%d %H:%M:%S')

		## Create the root logging object and get the name of the current module. (root)
		self.root_logger = logging.getLogger("")

		## Set the logging level for the root logger. (Can be overridden for each module.)
		if (self.logging_level.upper() == "DEBUG"):
			self.root_logger.setLevel(logging.DEBUG)

		elif (self.logging_level.upper() == "INFO"):
			self.root_logger.setLevel(logging.INFO)

		elif (self.logging_level.upper() == "WARNING"):
			self.root_logger.setLevel(logging.WARNING)

		elif (self.logging_level.upper() == "ERROR"):
			self.root_logger.setLevel(logging.ERROR)

		elif (self.logging_level.upper() == "CRITICAL"):
			self.root_logger.setLevel(logging.CRITICAL)

		else:
			print "Startup - bitCollector_framework.FrameworkSettings.initializeRootLogger - WARNING - Unknown logging level: " + self.logging_level + ". Defaulting to DEBUG."
			self.root_logger.setLevel(logging.DEBUG)

		## Replace the time and date formatter in the supplied log file name if applicable.
		self.log_file = re.sub(r'\$\(DATE\)', time.strftime("%Y-%m-%d", time.localtime()), self.log_file, count=1)
		self.log_file = re.sub(r'\$\(TIME\)', time.strftime("%H-%M-%S", time.localtime()), self.log_file, count=1)

		## Verify that the log file directory exists.
		if (os.path.isdir(self.abs_log_dir) == 0):
			os.makedirs(self.abs_log_dir)
			print "Startup - bitCollector_framework.FrameworkSettings.initializeRootLogger - WARNING - Log directory doesn't exists. Making."			
			print "Startup - bitCollector_framework.FrameworkSettings.initializeRootLogger - WARNING - Created log directory: " + abs_log_dir

		## Create the log file logging stream and configure it.
		for log_count in range(1000):
			try:
				temp_file = self.log_file + "_" + str(log_count + 1) + "." + self.logging_format
				if (os.path.isfile(temp_file) == 0):
					self.log_file = temp_file
					self.log_file_handler = logging.handlers.RotatingFileHandler(self.log_file, mode='a', maxBytes=1073741824, backupCount=99, encoding=None, delay=0)
					break

			except IOError:
				print "Startup - bitCollector_framework.FrameworkSettings.initializeRootLogger - ERROR - Unable to open: " + self.log_file + "."
				sys.exit()

		self.log_file_handler.setFormatter(self.log_file_formatter)

		## Only log to the file if specified.
		if (self.log_to_file == 1):
			if (self.logging_format == "html"):
				## Write the table header to the log file.
				temp_handler = open(self.log_file, 'a')
				temp_handler.write("<table border=\"1\"  width=\"100%\"><tr><th>Date & Time</th><th>Traceback</th><th>Level</th><th>Message</th></tr>\n")
				temp_handler.close()

			else:
				temp_handler = open(self.log_file, 'a')
				temp_handler.write("Date & Time,Traceback,Level,Message\n")
				temp_handler.close()

			self.root_logger.addHandler(self.log_file_handler)

		## Create the console logging stream and configure it.
		self.log_console_handler = logging.StreamHandler(sys.stdout)
		self.log_console_handler.setFormatter(self.log_console_formatter)

		## Only log to STDOUT if specified.
		if (self.log_to_stdout == 1):
			self.root_logger.addHandler(self.log_console_handler)

## Class Name: ThreadManager
##
## Purpose: Holds information pertaining to all running threads.
class ThreadManager():
	## Method Name: __init__
	##
	## Purpose: Initialize the platform-independent attributes as well as the correct platform-dependent object.
	##
	## Parameters: None
	def __init__(self):
		## Initialize the Logger for this class.
		self.logger = logging.getLogger(self.__class__.__name__)
		self.logger.debug("Entering BitCollector.ThreadManager.__init__()")

		self.thread_list = []

	def addThread(self, thread):
		self.thread_list.append(thread)

	def removeThread(self, thread):
		for each in self.thread_list:
			if (each.thread_id == thread.thread_id):
				self.logger.debug("Removing thread with ID each.thread_id" + each.thread_id)
				self.thread_list.remove(each)
				break

## Class Name: Platform
##
## Purpose: Hold information about the target machine.
class Platform():
	## Method Name: __init__
	##
	## Purpose: Initialize the platform-independent attributes as well as the correct platform-dependent object.
	##
	## Parameters
	## 1. tuple - A 6 part-tuple containing platform-independent information about the target machine.
	##    Index 0  - The type of OS running on the target machine. (Windows, Linux, etc) 
	##    Index 1  - The hostname of the target machine.
	##    Index 2  - The release # of the OS running on the target machine. (2.2.0, NT, 8, etc)
	##    Index 3  - The version of the OS running on the target machine.
	##    Index 4  - The machine CPU architecture (i386, AMD64, etc)
	##    Index 5  - Information about the processor in the target machine as a 3-part tuple.
	def __init__(self, tuple):
		## Initialize the Logger for this class.
		self.logger = logging.getLogger(self.__class__.__name__)
		self.logger.debug("Entering BitCollector.Platform.__init__()")

		## Replace unknown information ('') with "Unknown"
		for each in tuple:
			if (each == ""):
				each = "unknown"

		## Initialize the platform-independent attributes.
		self.system    = tuple[0]
		self.node      = tuple[1]
		self.release   = tuple[2]
		self.version   = tuple[3]
		self.machine   = tuple[4]
		self.processor = tuple[5]

		## Initialize the OS type attribute which will be populated below.
		self.os_type   = "unknown"

		## Initialize the platform OS-dependent attribute objects.
		## Mac OS
		if (re.search(r'mac', self.system.lower())):
			self.os_type = "mac"
			self.mac_platform = MacPlatform(platform.mac_ver(release='', versioninfo=('', '', ''), machine=''))

		## Linux/Unix
		elif (re.search(r'nix', self.system.lower())):
			self.os_type = "nix"
			self.nix_platform = NixPlatform(platform.linux_distribution(distname='', version='', id='', supported_dists=('SuSE', 'debian', 'redhat', 'mandrake'), full_distribution_name=1))

		## Windows
		elif (re.search(r'win', self.system.lower())):
			self.os_type = "windows"
			self.win_platform = WinPlatform(platform.win32_ver(release='', version='', csd='', ptype=''))

		else:
			self.logger.warning("Unknown OS type. Unable to perform OS-dependent logic!")

## Class Name: MacPlatform
##
## Purpose: Hold Mac OS-dependent information about the target machine.
class MacPlatform():
	## Method Name: __init__
	##
	## Purpose: Initialize the Mac OS-dependent attributes.
	##
	## Parameters
	## 1. tuple - A 4 part-tuple containing platform-independent information about the target machine.
	##    Index 0  - The release # of the Mac OS running on the target machine. (2.2.0, NT, 8, etc)
	##    Index 1  - Information about the running Mac OS version as a tuple.
	##        Index[1][0] - The version of the Mac OS running on the target machine.
	##        Index[1][1] - The dev stage of the Mac OS version running on the target machine.
	##        Index[1][2] - Whether or not the Mac OS version running on the target machine is a non-release version.
	##    Index 2  - The parenthesized portion of the version. (usually a codename)
	def __init__(self, tuple):
		## Initialize the Logger for this class.
		self.logger = logging.getLogger(self.__class__.__name__)
		self.logger.debug("Entering BitCollector.MacPlatform.__init__()")

		## Replace unknown information ('') with "Unknown"
		for each in tuple:
			if (each == ""):
				each = "Unknown"

		## Initialize the Mac OS-dependent attribute objects.
		self.release      = tuple[0]
		self.version_info = tuple[1]
		self.machine      = tuple[2]

## Class Name: NixPlatform
##
## Purpose: Hold Linux/Unix OS-dependent information about the target machine.
class NixPlatform():
	## Method Name: __init__
	##
	## Purpose: Initialize the Linux/Unix OS-dependent attributes.
	##
	## Parameters
	## 1. tuple - A 4 part-tuple containing platform-independent information about the target machine.
	##    Index 0  - The full distribution name of the Linux/Unix OS.
	##    Index 1  - The version of the Linux/Unix OS running on the target machine.
	##    Index 2  - The parenthesized portion of the version. (usually a codename)
	def __init__(self, tuple):
		## Initialize the Logger for this class.
		self.logger = logging.getLogger(self.__class__.__name__)
		self.logger.debug("Entering BitCollector.NixPlatform.__init__()")

		## Replace unknown information ('') with "Unknown"
		for each in tuple:
			if (each == ""):
				each = "Unknown"

		## Initialize the Linux/Unix OS-dependent attribute objects.
		self.distname = tuple[0]
		self.version  = tuple[1]
		self.id       = tuple[2]

## Class Name: WinPlatform
##
## Purpose: Hold Windows OS-dependent information about the target machine.
class WinPlatform():
	## Method Name: __init__
	##
	## Purpose: Initialize the Windows OS-dependent attributes.
	##
	## Parameters
	## 1. tuple - A 4 part-tuple containing platform-independent information about the target machine.
	##    Index 0  - The release # of the Windows OS running on the target machine.
	##    Index 1  - The version of the Windows OS running on the target machine.
	##    Index 2  - The service pack level of the Windows OS.
	##    Index 3  - The processor type.
	def __init__(self, tuple):
		## Initialize the Logger for this class.
		self.logger = logging.getLogger(self.__class__.__name__)
		self.logger.debug("Entering BitCollector.WinPlatform.__init__()")

		## Replace unknown information ('') with "Unknown"
		for each in tuple:
			if (each == ""):
				each = "Unknown"

		## Initialize the Windows OS-dependent attribute objects.
		self.release = tuple[0]
		self.version = tuple[1]
		self.csd     = tuple[2]
		self.ptype   = tuple[3]

## Classless Method Declarations

## Method Name: frameworkCleanUp
##
## Purpose: Wait for child threads to exit and perform Framework clean up
##
## Parameters
## 1. log_file       - The name of the log file to write the logging footer to.
## 2. logging_format - The format to in which to save the log file (CSV or HTML)
## 3. log_to_file    - A boolean tracking whether or not to log to the log file.
def frameworkCleanUp(root_logger, log_file, logging_format, log_to_file):
	root_logger.debug("Entering BitCollector.frameworkCleanUp()")

	while (threading.activeCount() > 1):
		time.sleep(1)

	## Only write the footer to the log file if file logging was enabled and the format was HTML.
	if (logging_format == "html" and log_to_file == 1):
		log_file_handler = open(log_file, 'a')
		log_file_handler.write("</table>")
		log_file_handler.close()

## Method Name: importBCModules
##
## Purpose: Dynamically import the BitCollector modules specified in the configuration file.
##
## Parameters
## 1. root_logger      - The logger from the main method.
## 2. additional_paths - The list of additional module search paths.
## 3. module_list      - The list of modules stored as dictionaries.
def importBCModules(root_logger, additional_paths, module_list):
	root_logger.debug("Entering BitCollector.importBCModules()")

	## Add the additional search paths for BitCollector modules.
	for each in additional_paths:
		sys.path.append(each)

	## Attempt to import each of the BitCollector modules.
	for module in module_list:
		for key in module:
			if (key == "name"):
				try:
					__import__(module[key])
					root_logger.info("Successfully imported module: " + str(module[key]))

				except:
					root_logger.warning("Unable to import module: " + str(module[key]))

## Method Name: main
##
## Purpose: Serves as the entry point into the script.
def main():
	## Parse the command-line arguments to get start-up options.
	config_path = parseCLA()

	## Parse the configuration file to determine runtime settings and to
	## initialize the FrameworkSettings object to contain all of the settings required to run the modules.
	framework_settings = FrameworkSettings(parseConfig(config_path))

	## Create a logger for methods called by main().
	root_logger = logging.getLogger("")
	root_logger.debug("Initialized root_logger")

	## Create a Platform instance to check the hardware and OS configuration.
	platform_details = Platform(platform.uname())

	## Dynamically import BitCollector modules specified in the configuration file.
	importBCModules(root_logger, framework_settings.additional_paths, framework_settings.module_list)

	## Loop through and call the main method within each of the dynamically loaded BitCollector modules.
	for module_dict in framework_settings.module_list:
		new_thread = InitializeBCModuleThread(framework_settings, platform_details, module_dict)

		## Force the main thread to wait for the child thread before terminating.
		new_thread.join()

	## Wait for child threads and perform clean up.
	frameworkCleanUp(root_logger, framework_settings.log_file, framework_settings.logging_format, framework_settings.log_to_file)

## Method Name: parseCLA
##
## Purpose: Parse through and validate the CLA needed to start the framework.
def parseCLA():
	## Initialize flow control booleans
	bool_help = 0
	bool_version = 0

	## Validate # of CLA.
	if (len(sys.argv) < 2):
		print "    Invalid Usage: Use " + sys.argv[0] + " -h to display the help."

		sys.exit()

	## Loop through each CLA and choose what to do based on the the arguments provided.
	for arg in sys.argv:
		temp = arg.lower()

		if (temp == "-h" or temp == "--help"):
			bool_help = 1

		elif (temp == "-v" or temp == "--version"):
			bool_version = 1

		elif (re.match("--?\w+", temp)):
			print "    Invalid Usage:     Use " + sys.argv[0] + " -h to display the help."
			sys.exit()

		else:
			config_path = sys.argv[1]

	## Print the help
	if (bool_help == 1):
		print "\n    Usage: " + sys.argv[0] + " [options] <config_path>"
		print "\n    Options"
		print "        -h | --help - Prints out this help."
		print "        -v | --version - Prints out the version you are using."
		print "\nconfig_file - The JSON file containing the settings for the script."

	## Print the version
	if (bool_version == 1):
		print "\n    " + _framework_version

	## Exit if the help or version was printed.
	if (bool_help == 1 or bool_version == 1):
		sys.exit()

	return config_path

## Method Name: parseConfig
##
## Purpose: Parse through the configuration file to determine runtime settings.
##
## Parameters
## 1. config_path - The path to the configuration file.
##
## Returns
## A tuple
##   Index 0 - The path to the file to write log entries to.
##   Index 1 - The default logging level to use when logging.
##   Index 2 - The list of modules. Each element contains the name and settings for one module. 
def parseConfig(config_path):
	## Initialize blank lists to store the additional paths and module dictionaries.
	additional_paths = []
	module_list      = []

	## Initialize booleans tracking if the required framework attributes are present.
	module_list_present      = 0
	additional_paths_present = 0
	log_file_present         = 0
	logging_format_present   = 0
	logging_level_present    = 0
	log_to_file_present      = 0
	log_to_stdout_present    = 0

	## Initialize booleans tracking whether the required module attributes are present.
	name_present       = 0
	parameters_present = 0
	
	## Initialize a boolean tracking whether or not to exit.
	bool_exit = 0
	
	## Initialize a boolean tracking whether or not to break out of the module loop.
	bool_break = 0

	## Initialize lists to store missing required configuration entries.
	missing_framework_config_entries = []
	missing_module_config_entries    = []

	## Open the configuration file for parsing.
	try:
		config_json = json.load(open(config_path))

	except IOError:
		print "Startup - bitCollector_framework.root.parseConfig - ERROR - Unable to open: " + config_path + "."
		sys.exit()

	except ValueError:
		print "Startup - bitCollector_framework.root.parseConfig - ERROR - The configuration file provided is not properly formatted JSON."
		sys.exit()

	## Parse through each of the key value pairs of the entire JSON payload.
	for key, value in config_json.iteritems():
		if (key == "log_file"):
			log_file_present = 1
			log_file = value

		elif (key == "logging_format"):
			logging_format_present = 1
			logging_format = value

		elif (key == "logging_level"):
			logging_level_present = 1
			logging_level = value

		elif (key == "log_to_file"):
			log_to_file_present = 1
			log_to_file = value

		elif (key == "log_to_stdout"):
			log_to_stdout_present = 1
			log_to_stdout = value

		elif (key == "additional_paths"):
			additional_paths_present = 1
			
			## Loop through each of the paths in the list.
			for path in config_json["additional_paths"]:
				## Loop through the attributes of each module and update the dictionary with those attributes.
				for key, value in path.iteritems():
					additional_paths.append(value)

		elif (key == "module_list"):
			module_list_present = 1
		
			## Loop through each of the modules in the list.
			for module in config_json["module_list"]:				
				## Initialize a blank dictionary to populate with the attributes of a module.
				current_module = {}
				
				## Reset the values of the booleans tracking the presence of the name and parameters attributes as well as the break boolean.
				name_present       = 0
				parameters_present = 0
				bool_break         = 0

				## Loop through the attributes of each module and update the dictionary with those attributes.
				for key, value in module.iteritems():
					if (key == "name"):
						name_present = 1
						current_module.update({key: value})

					elif (key == "parameters"):
						parameters_present = 1
						current_module.update({key: value})

					else:
						print "Startup - bitCollector_framework.root.parseConfig - WARNING - Unknown module configuration attribute: " + key

				if (name_present == 0):
					missing_module_config_entries.append("name")
					bool_break = 1

				if (parameters_present == 0):
					missing_module_config_entries.append("parameters")
					bool_break = 1

				## Break out of the loop if any of the required module attributes are missing.
				if (bool_break == 1):
					for entry in missing_module_config_entries:
						print "Startup - bitCollector_framework.root.parseConfig - WARNING - Required module configuration entry missing: " + entry
						
					print "Module will not be imported. See documentation for more info."
				
				else:
					## Add the dictionary containing all the module settings to the list of modules.
					module_list.append(current_module)

		else:
			print "Startup - bitCollector_framework.root.parseConfig - WARNING - Unknown framework configuration attribute: " + key

	## If any of the required configuration entries are not present, exit.
	if (module_list_present == 0):
		bool_exit = 1
		missing_framework_config_entries.append("module_list")

	if (additional_paths_present == 0):
		bool_exit = 1
		missing_framework_config_entries.append("additional_paths")

	if (log_file_present == 0):
		bool_exit = 1
		missing_framework_config_entries.append("log_file")

	if (logging_format_present == 0):
		bool_exit = 1
		missing_framework_config_entries.append("logging_format")

	if (logging_level_present == 0):
		bool_exit = 1
		missing_framework_config_entries.append("logging_level")

	if (log_to_file_present == 0):
		bool_exit = 1
		missing_framework_config_entries.append("log_to_file")

	if (log_to_stdout_present == 0):
		bool_exit = 1
		missing_framework_config_entries.append("log_to_stdout")
	
	if (bool_exit == 1):
		for entry in missing_framework_config_entries:
			print "Startup - bitCollector_framework.root.parseConfig - ERROR - Required framework configuration entry missing: " + entry
		
		print "Startup - bitCollector_framework.root.parseConfig - ERROR - See documentation for more info."
		sys.exit()

	else:
		## Return the configuration file name and level as well as the list of modules as a tuple.
		return log_file, logging_format, logging_level, log_to_file, log_to_stdout, additional_paths, module_list

## This will prevent main() from running unless explicitly called.
if (__name__ == "__main__"):
	main()
