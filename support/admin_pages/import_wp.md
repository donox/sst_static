### Procedure to Load a WP Backup
The process is described in the Nikola handbook at [Importing Wordpress](https://getnikola.com/handbook.html#importing-your-wordpress-site-into-nikola).
This page builds on that description but generally follows the procedure as described.

#### Generating and importing an XML dump of the site
In the Wordpress backend, go to **Tools/Export**.  It is a small issue, but because there may be updates 
to the site between the time a backup is created (around 4:00pm daily) and the time the xml dump is taken, 
it would be best to pull the xml dump around the same time as the backup if there is the possibility of 
a change to the site in the intervening time.
1. Use the "ALl" content button. 
2. In a terminal, navigate to the Nikola **project** (one level above the site where we normally run
   commands).
3. run **nikola import-wordpress /home/don/Downloads/sstxml.xml (path to your download)
4. At this point, you should be able to cd into the new_site and do a nikola build.
5. Assuming the build was successful, you can run nikola serve and should be able to see the 
   imported site <http://localhost:8000/pages/page-two/> though it will not have pics or navbar, etc. 
   It does establish that you have a successful import.
   
##### Delete "Old" Pages, Rename Page One
There will be a significant number of pages created whose filename is a set of digits.  These appear to 
be earlier saves in Wordpress.  They may be deleted.

There is also one page with no filename (just the extension ".md").  This is actually Page One and should be 
renamed (including the ".meta" file) as "page-one.md".  Also, update the slug in the ".meta" file.

#### Download Most Recent Backup from Google Drive
The db.gz file contains the SQL DB and is the primary file for getting the information 
needed to convert the WP photo ID's to the pathnames needed in Nikola.  The 'other' files 
contain all pictures and other files of possible interest.  

Because of a bug in the database backup/restore, the backup file will not successfully import into 
a MySQL DB without a minor fixup. The photo tables are defined to have a default date (eg., required), 
the backup has a default date of '0000-00-00' which is invalid.  To successfully import the db
file, you need to modify **all** occurrences of the date string. I generally set it to '2000-01-01' though 
anything will do.  Because of the large size of the file, most editors have trouble loading/modifying it.

There is a plugin (**wp_db_fix**) which reads the database file and
makes the needed corrections.  To use, move the input file into the support directory using the name
**db.sql** (or modify the code with a different name).  From a terminal, **cd** back to the normal site (this
is to get access to plugins).  Run **nikola wp_db_fix** which 
will take several seconds and should report several changes. You can **cd** back to **new_site**. It will
create a file **db2.sql** also in the support directory containing the modified file.  You may remove
them from the support directory when done.

#### Use Datagrip to Import the WP DB File
This creates the pics.csv file used by convert_shortcodes to map WP picture ID's to Nikola pathnames.
1. Open DataGrip and create a new schema ('s3' in this example).
2. In a console run the statement: **use s3;**
3. Right click on the schema in the database tree on the left and select **Run SQL Script**
4. Navigate to your database file created above and select it.  It should read the database,
   and you can follow progress in the terminal.
5. Create and run the query: **select t1.pid, t1.filename, t1.alttext, t1.imagedate, t1.description, 
   t2.path from wp_ngg_pictures as t1 
   join wp_ngg_gallery as t2 on t1.galleryid = t2.gid order by 
   t1.pid;** in the console and run it (ctrl-enter).
6. Right-click on  the console (with the result of the previous query) and select **Export Data**.
7. Navigate to the files directory of the new_site and select.  Select CSV (default) and no headers (default).
   Set the filename to pics.csv.
8. Create and run the query **select post_name, post_title from wp_posts
   where post_status="publish" and post_type='page';**   
9. Right-click on  the console (with the result of the previous query) and select **Export Data**.
10. Navigate to the files directory of the new_site and select.  Select CSV (default) and no headers (default).
   Set the filename to posts.csv.

### Import Images
This will copy the image files from the backup to the images folder.
1. Extract the files in the backup labeled 'others'. Navigate to the gallery folder and copy the **contents** 
   to the image folder (will take a while)
2. Open folder 'others2'. Again, copy contents.  Duplicate folders will merge content.
3. Repeat 'others3'
4. Repeat 'others4'
5. Copy del_thumbnails.py from existing site into new_site.  Edit file and modify pathname (**new_site**) if needed.
6. In a terminal: **python3 del_thumbnails.py**  (no '-m' argument).  It should delete a few hundred
   directories and probably 0 files.
   
### Save Zip Copies
In order to avoid rerunning import, etc., it is a good idea to grab a zip of the pages and images folders.
This will allow you to replace the active copies if they have been modified (e.g., shortcodes fixed, ...)
and the process goes awry somehow.  Can delete this step when/if importing becomes stable.
   
### Other Imports
Uploads and downloads from WP exist in some of the 'other' folders. Find and copy relevant content to
corresponding folders (look at existing site for guidance).  Alternatively, copy the content from the 
existing site to the new site and check if there is anything possibly missed and find a copy (probably on 
live site) and bring it over.

Check for proper pdf downloading.  Probably check after site is generating correctly, but the issue seems to be
a failure to capture all the pdfs (some are individual files in downloads folder - not directories) and
possible naming inconsistencies (e.g, Best_Books... vs BestBooks... ).  Look in Libraries, Birthdays, veterans...

### Copy Plugins, Themes, Support, SC_Templates, Conf.py 
1. Copy **plugins, themes, sc_templates, support folders** from the existing site to the new site. 
2. Copy Conf.py and replace copy in existing site.  Scan **conf.py** for instances of existing site and replace
   with new_site  (should be three that are paths - ignore them, site name).  Alternatively, rename existing site 
   to xxxOLD and rename new site to match old site.

### Run Fixes
If there are any fixes in fixes.txt, run nikola  wp_fixups_from_issues.


### Convert Shortcodes and Build
Run nikola convert_shortcodes.

If all goes well, run nikola build.

Run nikola serve and use browser to see if site has imported properly.

### Uploading to PythonAnywhere
The easiest way to update PA is to zip the pages, images, and gallery directories
and copy them using PyCharm remote host browsing (just drag and drop). It
will take a while (several minutes). Delete the existing directories and then from a bash console in PA, 
unzip the files.  Run **nikola build**.

   

   

