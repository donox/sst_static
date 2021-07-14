### Creating Pages Using MS Word Documents
Sunnyside Times can use input in the form of an MS Word document to create web pages.
The document may contain shortcodes to provide additional information.  It may also
use some Word style information such as bold and italics. 

This page describes the process for creating a story such as would occur in Resident
Told Stories (or other) beginning with a Word source document.

####Process Summary
The steps for creating a page beginning from Word are:

1. Create a regular Word document with the content and relevant annotations such as
pictures or title information.
2. Determine the name for the document and its placement in the file system.  
3. Create photos and slideshows referenced in document.  Generally, provide captions for individual
photos in the shortcode.  For a gallery, it is easiest to provide
caption and ordering information externally and let support make the necessary additional
files.
4. If the article is to appear on Page One or Page Two, provide instructions to Support.

####Creating the Word Source
Create the text content for the document.  Use headings (not title), bold, and italics
as desired. 

Insert author, title, and photo information shortcodes at the appropriate location in 
the document.  The easiest way to do this is copy/paste an existing shortcode
instance and modify it as necessary.  

#####Insert Title, Byline, Photo Byline
All these items use the same ("meta_info") shortcode and are generally added at the top. 
of the document.  

<span>\{\{% meta_info info_type="title" %}}xxxTITLExxx\{\{% meta_info %}}</span>

<span>\{\{% meta_info info_type="byline" %}}xxxAUTHORsxxx\{\{% meta_info %}}</span>

<span>\{\{% meta_info info_type="photo" %}}xxxPHOTOGRAPHERsxxx\{\{% meta_info %}}</span>

#####Insert Single Photo
Insert photos using the "singlepic" shortcode:

<span>\{\{% singlepic image="xxxIMAGExPATHxxx" width="400px" height="300px" 
alignment="center" caption="" title="" has_borders="False" %}}</span>

The **image path** is a path name beginning with "/image" (e.g., 
"/image/Art/artist/myphoto.jpg").  If it is an existing image, it should be able 
to be found on the website under **SYS_ADMIN/PAGES TO PHOTOS**.  If it is an image
to be inserted, identify the containing folder and provide a unique name within that 
folder. If a new folder is to be created, identify the parent folder and provide the 
new folder name and photo name.  

Other attributes such as *width* or *alignment* are optional.  They may be removed
from the shortcode for readability but that is not necessary.

#####Insert Slide Show
A slide show is the most complex entry as it requires an additional file for description of
things like the captions and slide ordering.  The easiest way to deal with a gallery is to
provide an independent written summary of what is needed along with the photos to be included
in the gallery. 

On the system, a gallery is a separately named folder.  Images within galleries are 
separate from individual images used with *singlepic*, so if an image is to occur in both
a gallery and as a singlepic, it is duplicated in the system. 

Reference galleries in the Word document with the "gallery" shortcode:

<span>\{\{% gallery gallery_name %}}</span>
