### Sunnyside-Times Content Editing Commands
In order to control the content on the website, editors need a vehicle to express that control. That
mechanism is a file, **commands.txt**, that is created in each content folder (exclusive of galleries, 
which have their own mechanism). 

The best way to learn to use these commands is to copy and modify an existing set (or example).

*[This capability is a work in progress.  Please help with suggestions, issues, ideas, ...]*

**WARNING:  Avoid the use of tabs in .txt files (commands.txt, meta.txt, xxx-template-story.txt, galleries' 
metadata.yml).**

**WARNING: Avoid the use of spaces in file names.  Both "-" and "_" may be used.**

###commands.txt
All commands.txt files share the same basic format.  They are **.txt** files in a simplified
yaml format (this need not be meaningful).  The file is structured as a series of individual commands, each
separated by a line consisting of **---** (three dashes).

Each non-separator line consists of a *key* terminated with a colon and space.  Everything after that to
either the end of line or a *#* character is a *value* associated with the key.  Anything following the *#*
to the end of line is a comment. 

The first command in any file is a single line with the key **command_set** and a value indicating the
primary purpose (and thus what kind of processing is to be performed) of the commands in the file.

###Command Sets
The key **command_set** tells the system what kind of processing is appropriate for the file.  Possible values
for this key are "top", "content", "story".  

"top" is a key value in a command.txt file occurring directly in the **SSTmanagement** folder.  It's primary purpose
is to set the identity of the person responsible for this group of commands (see identity below) and to specify
the folder to be processed and the purpose of the folder.  

"content" is a key value in a folder immediately within **SSTmanagement** and is used to identify the specific folder
within **SSTmanagement** to be processed and the general purpose of that folder.

"story" is a key value in a second level folder (identified in the *content* folder above) and identifies the folder
as containing the content for a specific story for the website.  \[At this time, *story* ] is the only such key value
but more are expected as more processing support is added. 

###Command: identity,  Command set:  (top, content, story)
All folders may contain an identity command.  If no identity command is set, the system administrator is assumed.
The identity command has the optional keys **person** and **send_log**.

The value of the *person* key is a name, known to the system of someone who is an editor or system administrator.
Currently known names are "don", "sam", "linda", "colleen".  

The value of the *send_log* key is either "True" or "False".  If send_log is True, then a log of the processing will
be emailed to each requesting person occurring in an identity command. 

###Command: all,  Command set:  (content)
The command *all* indicates that all sub-folders within a content level folder are to be processed.  If there
are multiple stories in the folder and some are not to be processed, then the command would be *process_folder* 
with a value giving the name of the folder to process.

###Command: process_single_folder, Command set: (top, content)
The command *process_single_folder* is used to select which folder at its level is to be processed. It may
occur more than once in a command_set.

###Command: story, Command set: (story)
The command *story* is the working command that handles a story destined for the site.  There are a number 
of variants including the ability to process docx files and template created files.  The specific work 
performed is determined by the content of the folder and specifications in the **meta.txt** file.  

There are three types of content, each optional:

1. **Story**.  There may be a single document resulting in a markdown file and ultimately a single web page.
A story may be either a *Word document* or it may be a *YAML file* that provides the content needed by a
pre-existing template.

2. **Photos**.  There may be an arbitrary number of photos which are generally referenced by an included
story, but, in fact, are independent and can be referenced from any other content.  If there are photos, there
must be a *photos.txt* file specifying the pathnames where the photos are to be stored in the site's 
*images* directory.  The photo.txt file is a list of pathnames for the photos.  Each photo in the folder
**must** match the last segment of a pathname in photos.txt.  Note that care needs to be taken on ensuring
filenames have no spaces and that capitalization matches. 

3. **Galleries**. There may be an arbitrary number of galleries of photos.  A gallery is in its own 
folder.  Each folder within the parent folder is assumed to contain a gallery.  The structure of a gallery
folder is described under the *SYS_ADMIN/Shortcodes* page. 




