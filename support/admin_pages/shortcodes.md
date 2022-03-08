#User Guide to Shortcodes Available in Sunnyside Times
This user guide lists the shortcodes available in Sunnyside Times for the creation of content.  Some
shortcodes are custom creations in SsT and others are provided by the underlying system. 

When using shortcodes, please be alert for issues/needs where there may be a more effective variant (such
as an additional argument).  We really want to improve the system to create something of maximum
convenience and understandability for the users.

##Custom Shortcodes
###Add Meta Information Shortcode
This shortcode adds things like titles and bylines.  We can easily add other such info as the need is 
identified.  

> **\{\{% meta_info info_type="title" %\}\}2 horse powered 2 tone Cadillac!\{\{% /meta_info %\}\}**

Note the space *before* the forward slash terminating the shortcode.

The **info_type** specifies what is to be added.  The choices are:

1. **title** which adds a title to the story/page.
2. **byline** which adds the list of writers to the page.  The result is a line starting with **Written by:** 
   followed by the content in the shortcode.  There is no need to put "By" or the like.
3. **photo** which adds the photo credits to the page.  Similar to byline, except that it applies to
    the photographers.
    
###Add Disposition Shortcode
This shortcode adds a note at the end of a story giving the date of publication.  (not implemented yet:) I will 
also record a target removal date and specify the ultimate disposition of the story (discard, archive, ...). 

> **\{\{% disposition post_date="date story published" remove_date="date to remove" on_removal="archive" %\}\}**

**post_date** (optional) specifies a date (typically in mm/dd/yyyy format) that the story is published.  It will 
be added to story in a small font as "published: date".
**remove_date** (optional) specifies a date when the story will be taken down (--undecided if this is a report for 
the admin to follow or is an automatic removal - probably the former).
**on_removal** (optional) is one of **archive** or **discard** telling the system what to do with the story
when it is removed.

###Links Shortcode
This shortcode provides the means to link (html "a" tag) items or locations in a document.  In particular,
it is used to add downloads such as pdf files and to link to either external or internal urls.

> **\{\{% links purpose="download" reference="url or document" target="new" display="button" display_text="Read More" %\}\}**

**purpose** (required) specifies the intent of the link.  Possible values are:

1. **download** indicates that the link specifies a document (reference attribute) that may be
downloaded by the user.  The document must occur in the *files* directory of the website. 
2. **transfer** indicates a transfer (launch) of an external website.  The *target* attribute 
may be used to indicate whether the new page should replace the existing page (default) or 
open in a new page.  When transferring to an different website, you must include the full url
(e.g., https://foo.com)

**reference** (required) specifies the url identifying the page or document the link goes to.

**target** (optional) specifies where to open a linked document.  If it has the value **new**, it 
will open in a new browser page.  Alternatively, it may use any of the attribute values specified
in the html spec for the target attribute. (Note that "new" simply duplicates the html value "_blank")

**display** (optional) specifies whether the link should display as a *button* or a *link* (default).

**display_text** (optional) specifies the text to display on the link or button.  If nothing is specified,
a button will display as "Go To" or a link will display as "here".

###Gallery Shortcode
The gallery shortcode defines a "gallery" of pictures.  Galleries are currently a bit of a 
work in progress. There are two parts to using a gallery:

1. Create the gallery itself.
2. Insert the gallery at the desired location in the story.

Inserting the gallery in the story simply requires inserting the gallery shortcode:

>**\{\{% gallery gallery_name %\}\}**

Creating the gallery requires the creation of a folder containing the actual images to be included in the 
gallery and the creation of a specifier file named **metadata.yml** which tells how the gallery is to be rendered.
An example of a metadata.yml file:
>---
>Gallery path: /galleries/some_dir_for_content
>name: IMG_0842.JPG  
>order: 0  
>---
>name: IMG_0843.JPG  
>caption: Photo Caption   
>order: 1  
>---
>name: IMG_0845.JPG  
>caption: Another Photo Caption  
>order: 2  
>---

The metadata.yml file has one entry for each photo with photos separated by "---".  Each line is
an attribute that has a name followed by a colon and space. The value of the attribute immediately
follows on the same line. Each photo *must* have a "name".  It may optionally have a "caption" and/or
an "order".  Additionally, one entry *must* have a path name where the gallery will be saved 
in the system (Ideally, the gallery path would not be in a photo entry, but for technical reasons
fixing that would require more effort than its worth). 

*The actual display of the gallery is handled by a "Lightbox" named "baguetteBox".  Additional 
description can be found [here](https://getnikola.com/handbook.html#images-and-galleries).*

###Singlepic shortcode
The singlepic shortcode is used to insert a single image into a page.  It closely mirrors the Wordpress singlepic
shortcode.  The major difference is that images are identified by pathname rather than id.

> **\{\{% singlepic image="/images/Art/artists/WhilliamsHalloween.jpg" width="400px" height="300px" 
> alignment="center" caption="" title="" has_borders="False" %\}\}**

#####**"image="**
Image provides the path to the image. All images are stored in a local directory named
**images** which is the parent directory for the path.  The remainder of the path is set
by whatever layout you use for images.  The initial structure reflects the storage
location used by Wordpress at the time of importing.

#####**"width=", "height=", "alignment="**
Width and height of the image are set as was done in Wordpress.  The default value in 
each case is 300px. Alignment is the same as in Wordpress (left, right, center).  The 
default will generally be left as set by the browser when placing the image. 

#####**"title=", "caption="**
Title and caption are optional, but the intent will be to take them from the photo
metadata if they exist.  A title or caption specified in the shortcode will supercede
something contained in the photo.

#####**"has_borders="**
By default, individual pictures have a border.  For cartoons and similar fill-ins, it often
looks better without a border.  In that case, adding the has_borders attribute and setting it
to "False" (or "No") will remove the border.  

###Child_Links Shortcode
This shortcode generates a list of links to the child pages of a page (such as Stories by Residents).  Pages 
are listed in time sorted order with most recent first. The name of the file (generally also name of the article) 
is used as the link name.

> **\{\{% build_links_to_children %\}\}**

This shortcode currently has no arguments or other specifiers though developing them seems reasonable.

###Layout Shortcodes
These shortcodes provide the ability to specify layout for a document.  It is based on the CSS
Flexbox model which is described in 
[this basic tutorial](https://www.quackit.com/css/flexbox/tutorial/flexbox_introduction.cfm).

The general idea is to place parts of a web page (think picture, or a few paragraphs of text) in 
a container that specifies how to organize the content such as in a row or a column.  While the
Flexbox is a very general and powerful facility, our use is typically much more limited.

Each container (*box*) can specify how other containers (*boxitem*) that are contained within it
are arranged.  Each contained item (*boxitem*) itself contains arbitrary content excluding other
boxes or boxitems.  

Care needs to be exercised to ensure that boxitems do not overlap one another and that 
all boxitems are properly contained within a box

> **\{\{% box direction="row" %\}\} xx boxitems xx \{\{% /box %\}\}**

> **\{\{% boxitem  %\}\} xx content xx ** \{\{% /boxitem %\}\}**


#####**"direction="**
The (optional) direction parameter has a value of **"row"**, **"row-reverse"**, 
**"column"**, or **"column-reverse"**.  The default value is *row*.  *Row* specifies
left-to-right, *row-reverse* specifies right-to-left.  *Column* specifies top-to-bottom
while *column-reverse* specifies bottom-to-top.




