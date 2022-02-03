### Source Material Control and Google Drive

The primary means of providing source material for the web is to construct the material on the local
editor's computer and place it in a directory on Google Drive where automated processes can retrieve
it and organize it and add it to the site itself.

On Google Drive, the folder **SSTmanagement** serves as a repository for managing material prior to its
being added to the site itself.  There is a subdirectory, **NewContent**, for managing stories and photos.
The use of NewContent is described in this document.

####Process Summary
*This summary assumes a "normal" story with potentially pictures or slideshows.  Other types of content
may be handled differently.*

The general strategy is for the developing editor to create a file folder on his/her local machine and 
to collect all content for a particular story in that folder.  When it is ready to be submitted for 
publication, the editor simply drags the entire folder onto Google Drive.  

1. The name of the folder should probably correspond to the "slug" (last element of the pathname) though
the system does not (currently) use it.  
2. The story in the folder is a docx document with a name corresponding to the slug.  It is created in 
accordance with [Word-based Source Documents](pages/admin/word_based_input/).  Note that the file name
within the website will correspond to the slug, not the filename in the folder, thus it is a good idea
to make the name of the docx file correspond to the slug.
3. Photos in the story as individual photos (not slideshows) are in the folder with a filename corresponding 
to the photo slug. Because a full pathname is needed in order to place the photo in the proper directory, there 
is an additional *text* file named **photos.txt**.  The content of the file is a list of photo pathnames,
one pathname per line.  Note that the last element of the pathname must correspond to the slug for a photo file.
It is assumed that all photos are of type *jpg* (may be able to relax this constraint in the future).
4. Each gallery used in the story is in its own subfolder with a name corresponding to the slug for the gallery.
    1. Each photo in the gallery has a filename corresponding to its slug.
    2. Because more information than just a pathname is required for a gallery (such as order), their is an
    associated file containing that information.  It is named **metadata.yml** and follows the format described
    in [Shortcodes](pages/admin/shortcodes/).  The easiest way to create one is to copy another one and change
    the entries as appropriate.  
5. There is another specifier file named **meta.txt** that contains information about the story.  In particular, 
it specifies the path to the directory containing the story (e.g., "/pages/cool-stories-index/staff-profiles/") 
and the slug for the story itself (e.g., "a-very-busy-man").  Note that the directory contains and ends with
a slash and the slug has no slashes.  There can be a variety of other useful information for guiding the 
system.  The *samples* directory on Google Drive (*SSTManagement/Samples*) contains an example that can be 
copied and modified.


