#Guide to SST_UTILS Support for Building SsT
####Index
[Google Drive Top Level Folder](#top-level)<br>
[Content Related Folders](#content-folders)<br>
[Processing MS Word Documents](#content-word)<br>

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
<h2 id="#top-level"/>
This folder provides the primary location of all content being developed for addition to SsT.  

1. It contains a 
top level command file: **commands.txt** (described in System Commands mentioned above).  In order to allow different
users to utilize SSTmanagement without interfering with one another,  There may be additional commands.txt files where
the filename is prepended with a string **xxx_** where xxx is generally a user name and is set in a Python environment
variable called **USER_PREFIX** (set in the run configuration within PyCharm).  If there is no USER_PREFIX set, then 
the default command file is commands.txt and is the preferred means of managing the actual system updates.

    Note that using a prefix allows independent commands.txt files, the changes called for in any command set do modify
    the sst_static directory on the running machine which may lead to conflicts when there are multiple command sets being 
    used.  NOTE:  we need the ability to run in a *test mode* that does not modify the sst_static directory.

2. It contains multiple content folder(s).  The commands.txt file in use contains a **change_folder** command that 
allows the user to select among several potential folders to serve as the *top level* for processing.  There are 
(currently) two primary folders selected in the change_folder command.  The first is **Content** which is a 
structure for most ordinary web pages.  The second is **RecurringUse** which is intended for content that is 
frequently updated and posted again to the website such as this documentation or Sunnyside Clubs.

3. Within **Content** are multiple folders for processing web pages.  The primary folder for content intended for
actual deployment is **NewContent**.  Sub-folders placed here will be processed and deployed to the live site.  Other
folders such as **NewContentTest** and **NewContentDev** are intended for system development and not live deployment.

4. Within **Recurring** use are folders intended for live deployment.  When updates are made to files within
a subfolder, the corresponding command files may be run to update the live site.

4. It contains a **UserData** folder which contains the files with user lists that build the input for the **Nikola 
make_user_logins** command. 

5. There are other folders currently not used by sst_utils such as a Samples folder to contain samples of various
control files.
 
####Sst_utilities Setup
As of this writing, sst_utils is run in development mode within PyCharm.  Since sst_utils is under active
development, this document may change and/or not be current.  Training on actually running sst_utils is currently
outside the scope of this document.

#####Using User Identifiers
* **USER**. Each running user has a system provided environment variable **USER**.  sst_utils uses this to 
determine machine specific dependencies specified in the config file (see below).
* **USER_PREFIX**.  This is a(n optional) Python environment variable specified in the run configuration of PyCharm.
It is prepended to *commands.txt* to identify the specific command file to be used in a particular run.

##Content Folders
<a id="#content-folders"/>
Content folders contain the content and instructions for processing a set of content (pages, photos, ...) to be 
added to sst_static.  Every folder must contain a **commands.txt** file to guide the processing.  A **meta.txt** 
file is required if the content will create or update the website.  Folders that do not contain a *meta.txt* file
guide the processing (such as indicating a group of folders to be processed) but do not affect the website directly.

###Content Folders for MS Word Documents
<a id="#content-word"/>
A folder to process a MS Word document consists of (Note: avoid the use of spaces in filenames):

1. **commands.txt** file.  This is usually a simple file that can likely be copied from another story folder unchanged.
2. **meta.txt** file.  This is the primary folder controlling placement of the story on the site.
3. **xxxxxx.docx** file.  This contains the actual story and control information in the form of shortcodes.
4. any number of **yyyy.jpg** photo files
5. any number of gallery sub-folders 

A gallery sub-folder consists of:

1. **metadata.yml** file.  This specifies data about the photos in a gallery including captions and ordering and the 
location on the system where the gallery is to be stored.
2. any number of **yyyy.jpg** photo files

A typical *meta.txt* file looks like this (do not include tab characters in the file):
```
    .. title: It's Been TWO Years
    .. slug: its-been-two-years
    .. date: 2022-03-24
    .. description: linda_test
    .. path: pages/senior-life-information/
    .. photo-path: pages/senior-life-information/
    .. xxxx: Yet another attribute
```

**path** specifies the folder where the story will be placed and also the url where a user can reference it on the 
website.<br>
**slug** specifies the name of the file and is appended to path to complete the url.
**photo-path** specifies the photo folder where photos are to be placed.  The name of the photo file is the name
used in storing the photo and should not include spaces or punctuation characters other than "-" or "_".<br>
