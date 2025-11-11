# A note on running command-line scripts
.bat scripts are sequences of command line commands.
They can usually be executed by clicking on the .bat file in the file explorer.
In this case, the working directory is the directory where the .bat file is located.
If clicking does not work, start the command line,
navigate to the containing directory of the .bat file
and type the name of the file (e. g. install.bat), then click "Enter".

# Installation
Run the script "install.bat" to install the required Python libraries
which are specified in the file "requirements.txt".

# Configuring
The configuration file should be called "config.json" and stored in the working directory.
It should contain a JSON object with a field "inputDirectory" pointing
to the corpus files from which the dictionary will be constructed.
The configuration file of the CorpusEditor program can be used as well.
Remember that backslashes should be escaped (prefixed with another backslash) in JSON.

# Usage
Run the script "DictionaryGenerator.bat" to run the application.

# Output
The output file "Dictionary.json" will be placed in the working directory.
An existing "Dictionary.json" file in this directory will be deleted.
If no "Dictionary.json" has appeared in the directory after the program
has been executed, this is likely to mean an unexpected error has occurred.

# Logging
The program will create a directory "logs" in its topmost directory.
It will document inconsistencies in the XML files which sometimes
need to be corrected manually (if marked as ERROR - not as WARNING or INFO).
Correcting them involves editing XML manually and is not required to run
the program successfully.
