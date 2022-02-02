### Sunnyside-Times Manage User Logins
All residents, staff listed in the staffing directory, and members of the Horizon club are eligible for logins
to Sunnyside-Times.  Each group is created from source data provided by Sunnyside.  

1. Residents - Sunnyside Resident Phone Directory - an Excel (.xls, not .xlsx) file.
2. Staff - Sunnyside Staff Directory - an Excel file.
3. Horizon Club - 

Each of these lists is in a different format and must be processed separately and combined into a single 
unified list for updating the system. When a new spreadsheet is received, it can be processed independently 
of the others and then combined to produce a revised list for the system.

The Google Drive folder **SSTmanagement/UserData/** contains both the master spreadsheet and a processed copy 
*csv* file for each group.

All groups are (at least partially) processed using sst_utils in which there are settings to determine 
how to proceed. 

####Resident Logins
The resident phone directory is sufficiently consistent that it can be fully processed by the system.  Simply
add the latest version to /UserData/ and note its full name (the document name includes the date).  Set 
the document name in sst_utils.  Note that the document name may include a period ('.') after 'Directory' 
which is easily missed.  Set the appropriate selectors to True and run them.

If everything proceeds normally, a revised *residents.csv* file will appear in /UserData/ containing a list
of names of all residents.  

It is useful to scan the source spreadsheet to ensure all names follow the standard pattern.  If the entry
refers to a couple, the first names are separated by an ampersand.  If the resident prefers a nickname, it
is included in quote marks following their formal name.  So long as the entry conforms to this pattern, the
system will handle it properly.  

In the event that it is necessary to modify an entry, the spreadsheet must be downloaded (it cannot be 
edited in Google Docs), the changes made, and saved as a **.xls** file. It can then be uploaded again.

####Staff Logins
The staff phone directory is not consistent enough to be edited automatically, though many of the entries
can be retrieved with an Excel formula (=left(B5, find(",",B5)-1) assuming the formula is in cell E5.  The
system assumes that column "E" will contain all result data.  Once entries retrievable by formula are identified,
scan the spreadsheet manually picking up any missing names (put them in any unused cell in the column) and 
correcting any cases where the formula took more an one name.  

Once all staff members have been accounted for, copy the entire column and paste it back using *Paste Special* 
to paste the text and remove formulas.  There may be cells containing 'nan' or that are empty.  They may be
ignored and the system will handle them.

Save the spreadsheet as an **.xls** file and upload it to /UserData/.  Enable processing of the staff list
in sst_utils and run the program producing the file *staff.csv* in /UserData/.

####Horizon Club Logins
TBD

####Creating the Combined System Login File
TBD

