#Website Source Management User Guide
This user guide captures the operating procedures and other information used to manage the workflow of website
source documents including text, photos, and uploadable/downloadable content.  **It is a work in progress and
should be updated on an ongoing basis to reflect current operating processes.**

##Roles Involved in Creating Content
This document describes the source development process in terms of roles.  An individual person my play multiple
roles and multiple persons may perform a single role.  It is assumed that the association of persons to roles
occurs at a level outside these documents.  These roles are:

1. **Writer**.
2. **Editor**.  This is a person responsible for updating the information for general content, appropriateness, etc.
This role may or may not provide information such as shortcodes needed by the system to work.
3. **Technical Editor**. This person is responsible for ensuring the content is properly structured for input
to the system.  This includes such things as ensuring that shortcodes are added where necessary, filenames and
their directories are chosen, photos are in an appropriate format with titles, captions, etc., and other items
of a more technical nature.  This role does not require access to the backend of the system itself.
4.  **System Admin**. This role is responsible for any actions needed to incorporate the content in the system
and ensure that it is loaded and displayed correctly.
5. **Reviewer**. This (more informal) role is a checking role to verify that a particular addition is added
consistent with the original writer's and editor's intent.

##Word-based Source Documents
The primary source of user created content is presumed to be in the form of MS Word documents (or Libre Office, etc).
These may be provided by the originating writer or converted by an initial editor.   Whether embedded in the document
or provided by other means, support information such as photos, titles, bylines, etc. may accompany the document.
Alternatively, editors may identify any needs and collect such information.

Writing and non-technical editing processes are outside the scope of this document.

###Technical Editing
An unmodified Word document should be handled by the system without failing, though we are assuming that all
documents have at least a title and preferably an author attribution.  It **must** have a filename and directory
where it is to be located.  The filename must be unique within the directory.  If it contains photos - either 
individually or in a gallery, those photos must also have names and directory locations for placement.  

The process of technical editing is responsible for adding (or checking) shortcodes to the document.  In particular, 
this role is responsible for verifying directory locations for files and ensuring that filenames are unique in the
corresponding directory.  This role is also responsible for constructing the **yaml** files needed to create 
galleries. 

***Note that we don't have a way to specify the filepath for a story in a shortcode.***  Until more automated means
are available, this role passes all files to the System Admin for actual inclusion in the system. 

###System Admin
For content related activities, this role is responsible for the actual uploading the content onto the site and running 
the necessary build procedures for deployment. 





