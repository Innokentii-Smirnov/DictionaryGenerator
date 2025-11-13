# A note on running command-line scripts
.bat scripts are sequences of command line commands.
On Windows, they can usually be executed by clicking on the .bat file in the file explorer.

If clicking does not work, start the command line,
navigate to the containing directory of the .bat file
and type the name of the file (e. g. "install.bat"), then click "Enter".
It is also possible to type the full name (with the directory) of
the .bat file instead of navigating to its directory.

# Working directory
If the .bat file has been started by clicking on it, the working directory is the directory
where the .bat file is located, i. e. the topmost directory of the DictionaryGenerator.

If the .bat file has been executed on the command line, the working directory is the
directory from which you ran it.

# Installation
First, install the Python interpreter.
Do not forget to tick "Add Python to PATH" in the installer!
https://www.python.org/downloads/

Run the script "install.bat" to install the required Python libraries
which are specified in the file "requirements.txt".

# Configuring
The configuration file should be called "config.json" and located in the working directory.
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
The program will create a subdirectory "logs" in the working directory.

The log "\_\_main\_\_.log" will contain an appropriate message
if the run has been completed successfully.

The other logs document the processing of the XML files
with informational messages (INFO) and
specify issues detected in the XML files which sometimes
need to be corrected manually (if marked as ERROR, not just as WARNING).
Correcting them involves editing XML manually and
is only recommended for experiences users.
It is not required to run the program successfully;
the morphological tag of the problematic word
will be ingored and the following words in the text
will be processed in the normal way.

The log "skipped_files.log" lists the files which could not have been
processed due to more serious, unexpected errors (perhaps in the program itself
and not in the XML files) and will be empty if all files were processed successfully, which should be the normal case.
