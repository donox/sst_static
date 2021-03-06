### Sunnyside-Times Operating Commands
Commands to maintain the system are implemented by **plugins**.  There are many plugins built
into Nikola and they can be referenced [here](https://getnikola.com/handbook.html).  This page
is more concerned about the commands used in the day-to-day operation and maintenance of the site.

Commands are run on a command line in the directory containing the site.  The project directory is
**sst_static/**, and the site within that directory is **sst/**.  Commands are of the form **nikola 
command args**.  Most commands needed do not normally require any args.

####nikola new_residents
The new_residents command creates a page which is generally added to Page One identifying the new
residents.  It uses a definition file **new_residents.yaml** that is maintained in the 
**sst_static/support/work_files/** directory.  The result are two files: **new-residents.html** and 
**new-residents.meta** in the pages directory of the site.

It can be updated manually or, preferably, automatically updated (software yet to be written) from
an available primary source. 

####nikola build_photo_usage
This command supports maintenance of the site, particularly by the content managers.  When run, it adds
two menu items to the Sys_Admin menu.  **PHOTO USAGE DATA** provides some summary statistics such as the 
number of pages and galleries, the number of unused pages and galleries, etc.  It also provides a list of
urls for all unused pages and galleries.  **PAGES TO PHOTOS** is a searchable listing that maps each page
to the photos and galleries that are referenced by it.  

####nikola process_docx_files
This command converts a docx file into a .md file.  There is a directory (docx_pages) under 
support.  Docx files are placed in that directory along with a corresponding meta file.
When this command is run, it creates a .md file also in that directory. A copy of that
created file is placed in the appropriate directory in **pages** (the .md file is no
longer needed).  In general, once a file has been processed, it may be removed as the 
converted file in the pages directory will serve as the new master file. 

The .meta file has a path attribute that gives the directory to which the .md file is
to be copied (e.g., ".. path: /pages/cool-stories-index/resident-told-stories/" ).

We assume that all photos and their appropriate locations are communicated separately. 

####nikola pages_in_migration
The pages in migration command is intended to support files that may be created or modified outside
the pages directory.  This is primarily intended for pages that may need to be modified during the 
period while nikola and Wordpress sites are running in parallel.  It is also useful for creating
new instances of existing pages before they are updated to the production site.

Running pages_in_migration will replace any instances of files of the same name that already exist
in the pages directory.  Pages to be migrated are maintained in the **migrating_pages** directory. 
Pages in the **support/admin** directory are also processed to update sys_admin documentation.

####nikola multi_pages
The multi_pages command is used to build Page One, Page Two or other similarly complex pages.  Each
such page is described by a folder named the same as the target page being created.  The structure
of the files in that folder is described under the **Multi-Story Pages** menu item.

####nikola make_user_logins
The make_user_logins command generates the **user_logins.js** file in the **themes/sst/assets/js/** 
directory that is used to verify users.  The generated file is a javascript object containing an
encrypted list of usernames and user passwords.  The source for the file is the **users.csv** file
in the **support** directory.

Entries in the users.csv file are the user name possibly followed by a password.  If no password
is provided, the default **Sunny** password is used. 

####nikola convert_shortcodes
The convert_shortcodes command processes all shortcodes contained in the source files into appropriate
html or other content.  The shortcodes are described [here](../shortcodes/)

####nikola wp_db_fix
This plugin reads a Wordpress database located at **/support/db_in.sql** and corrects records 
containing an invalid default date.  A new sql file is written to **/support/db_out.sql**

####nikola build
The build command is the Nikola provided command to build the site.  **nikola build -a** can be used 
to force nikola to rebuild the site in its entirety. Otherwise, nikola attempts to build only those
pages that have been modified, making it very fast.

The normal sequence for creating/updating a site, after making any desired changes is:

1. nikola new_residents
2. nikola pages_in_migration
3. nikola convert_shortcodes   
4. nikola multi_pages
5. nikola build

At that point the new site is constructed, deployed, and live (assuming there is a running web server).



