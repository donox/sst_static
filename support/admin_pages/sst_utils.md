#Guide to SST_UTILS Support for Building SsT
This  guide describes the processes and support provided by the sst_utils application code for maintaining
SsT itself.  sst_utils is an independent capability for sys_admins and/or developers that manages the 
SSTmanagement folder on Google Drive and preforms the initial processing for new content and other 
sources of system data such as user login lists, etc. 

In particular, it implements the command processing described in 
[System Commands](https://sunnyside-times.com/pages/admin/editor_commands/ 'System Commands'). It also supports
the processing of the SS provided lists of users (residents, staff, Horizon Club).

##Structure of SSTmanagement on Google Drive
Since sst_utils provides the interface to Google Drive, the assumed structure is important.

###SSTmanagement - Top Level
This folder provides the primary location of all content being developed for addition to SsT.  

1. It contains a 
top level command file: **commands.txt** (described in System Commands mentioned above).  In order to allow different
users to utilize SSTmanagement without interfering with one another,  There may be addition commands.txt files where
the filename is prepended with a string **xxx_** where xxx is generally a user name and is set in a Python environment
variable called **USER_PREFIX** (set in the run configuration within PyCharm).  If there is no USER_PREFIX set, then 
the default command file is commands.txt and is the preferred means of managing the actual system updates.

    Note that using a prefix allows independent commands.txt files, the changes called for in any command set do modify
    the sst_static directory on the running machine which may lead to conflicts when there are multiple command sets being 
    used.  NOTE:  we need the ability to run in a *test mode* that does not modify the sst_static directory.

2. It contains **NewContent** folder(s).  The actual name of the folder is specified in the controlling commands.txt.  By
having multiple commands.txt files (with appropriate USER_PREFIXes) and corresponding NewContentXXX folders, it's possible
to have several sets of content under development at one time.  

3. It contains a **UserData** folder which contains the files with user lists that build the input for the **Nikola 
make_user_logins** command. 

4. There are other folders currently not used by sst_utils such as a Samples folder to contain samples of various
control files.
 
####Sst_utilities Setup
As of this writing, sst_utils is run in development mode within PyCharm.  Since sst_utils is under active
development, this document may change and/or not be current.

####Using User Identifiers
* **USER**. Each running user has a system set environment **USER**.  sst_utils uses this to determine machine
specific dependencies specified in the config file (see below).
* **USER_PREFIX**.  This is a(n optional) Python environment variable specified in the run configuration of PyCharm.
It is prepended to *commands.txt* to identify the specific command file to be used in a particular run.

##NewContent Folders
NewContent folders contain the content and instructions for processing a set of content to be added to sst_static.  A
commands.txt file is required in each folder to guide the processing.  A meta.txt file is required if the content will
create or update a  page in the sst_static pages directory (including indirectly such as a docx file).  Photos in
a folder should be referenced by a *singlepic* shortcode in the source document.  Additionally, there may one or 
more subfolders containing a gallery of photos.

