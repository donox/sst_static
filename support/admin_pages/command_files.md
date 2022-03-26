### Sunnyside-Times User Content Management Command Files
Command files are used to control the processing of website content.  They are interpreted by
the *command processor* in sst_utils and control such things as processing docx files, placing photos
in the proper directory, etc. 

###Command Sets

There is one command file in each content directory with the name **commands.txt**.  It is a **YAML** file
containing a series of specifiers for work to be done.  There are 3 types of command.txt file - each known 
as a **command_set**. 

1.  **Command_set: top**.  This command_set is used at the SSTmanagement folder level and identifies the subfolder
that contains the content to be processed.  It's primary purpose is to determine the actual content
folder to be processed thus allowing a variety of other folders (such as backups, ...) to exist without
causing confusion.  There may actually be multiple *command.txt* files each with a specific preamble
such as "don_" (thus don_commands.txt) to allow multiple users to develop and maintain content without
conflicting.  The preamble is set as a system enviornment variable ("USER_PREFIX").
2. **Command_set: content**. This is a second level command_set which is used to control a number
of folders each containing content to be processed.  It's primary purpose is to allow the user to 
select among a group of folders being worked on simultaneously without requiring a lot of folders 
to appear at top level.  
3. **Command_set: story**.  This is a command_set for an actual folder to be processed presumably 
resulting in new content being added to the website.

###Commands.txt Structure
The commands.txt file is structured as a collection of commands (or command_set at the top), each
separated by a line containing "**---**".  The file also begins and ends with this separator.
Each command group begins with a **command:** ("command_set" in the first group).  The value 
following the command gives the specific command to be executed. Additional lines immediately
following a command give the parameters to the command and their values.  Anything on a line following
a **# ** is a comment and is ignored.

