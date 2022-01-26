#User Guide to Managing the Website for Sunnyside Times
This user guide captures the operating procedures and other information needed to create, operate, and maintain
the Sunnyside Times.  **It is a work in progress and should be updated on an ongoing basis to reflect current
operating processes.**

Each major process is described in its own document.  Below are short summaries and links to the documents.

##Content Creation
Much of the work of content creation lies outside of the actual work of developing and maintaining the website.
Such things as working with writers or managing photos (prior to the addition to the site) are complex processes
in their own right deserving their own documentation.  They are not directly addressed in this guide.

###Document Creation
There are a number of forms of source documents that can be used to create content for the web.  Each source format
may involve its own process.  The two primary formats are a structured **Word document** and a **Markdown document**.
Other forms include **HTML** documents and specialized documents controlling things like organization and layout
where appropriate.  These are typically **YAML** documents. Use of HTML or YAML documents are generally described
along with their usage procedures.  Lastly, documents may be *unformatted* meaning they are used as is without
processing by the website itself.  These include things like **pdf's** or similar documents.

####Word Document as Source
MS Word format is presumed to the be primary medium for creating web content.
[Creating Pages Using MS Word Documents](../word_based_input) describes the
mechanics of creating a suitable Word document.
[Managing Word-based Source Documents](../word_based_source_control)
describes the processes used to manage the workflow.

###Adding and Removing Users
The file **users.csv** in the **admin** directory is a list of all permitted users of the system.  The plugin 
**make_user_logins** converts this file to an encrypted list (**user_logins.js**) that loads as an asset to the 
running system.  It
is initially presumed that all users share the same password.  When a user logs in to the system and provides
a password, the system encrypts both the user name and the provided password.  It checks to see if the encrypted
pair is in the provided list to determine if the user can access the system.

To update the user_logins.js file, run the command **nikola make_user_logins**.  

When a user logs in, a cookie ("username") is set associated with the website.  The cookie expires after
six months and the user will need to log in again. 

###Backups
Source code required for the site is maintained in **github**.  Maintaining backups of site content is more 
problematical.  There are multiple instances of the content beginning with primary documents such as Word 
and continuing on to the generated HTML that is displayed.  

[Web Source Control](../website_source_control) contains
the processes for managing source or content for the site.  The basic idea is that responsibility for 
the primary source (such as Word or photos) belongs to Editors and Technical Editors and is generally done
using Google Docs.  The System Admin is responsible for backups of material on the site itself.  These are in 
those folders such as Pages, Images, Files that are used to build the site.  

Until an automated process is implemented, the System Admin will make a compressed copy of relevant folders
and copy them to Google Drive.  




