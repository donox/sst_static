#User Guide to Shortcodes Available in Sunnyside Times
This user guide lists the shortcodes available in Sunnyside Times for the creation of content.  Some
shortcodes are custom creations in SsT and others are provided by the underlying system. 

When using shortcodes, please be alert for issues/needs where there may be a more effective variant (such
as an additional argument).  It is highly desired that we improve the system to create something of maximum
convenience and understandability for the users.

##Custom Shortcodes
###Child_Links Shortcode
This shortcode generates a list of links to the child pages of a page (such as Stories by Residents).  Pages 
are listed in time sorted order with most recent first. The name of the file (generally also name of the article) 
is used as the link name.

> **\{\{% build_links_to_children %\}\}**

This shortcode currently has no arguments or other specifiers though developing them seems reasonable.

###Gallery Shortcode
The gallery shortcode defines a "gallery" of pictures.  Galleries are currently a bit of a 
work in progress. There are two parts to using a gallery:

1. Create the gallery itself.
2. Insert the gallery at the desired location.
u
Inserting the gallery simply requires inserting the gallery shortcode:

>**\{\{% gallery gallery_name %\}\}**

Creating the gallery requires the creation of a folder containing the actual images to be included in the 
gallery and the creation of a specifier file named **metadata.yml** which tell how the gallery is to be rendered.
An example of a metadata.yml file:
>---
>name: IMG_0842.JPG  
>order: 0  
>Gallery source page: '../../../PycharmProjects/sst_static/sst//pages/activities-index/resident-led-activities-index/indoor-games/bridge.md with gallery name - Gal17160'  
>---
>name: IMG_0843.JPG  
>caption: Photo Caption   
>order: 1  
>---
>name: IMG_0845.JPG  
>caption: Another Photo Caption  
>order: 2  
>---

Note that the first entry contains the path name to the internal source page containing the gallery
reference.  This is provided to allow the easy removal of the gallery by identifying the locations
where it is used.   There may be more than one **Gallery source page** entry.  Captions for an image
are taken from the photo meta data by the package we use to display an image.


*The gallery shortcode is a somewhat modified version of a system provided experimental shortcode,
thus accounting for some of its eccentricities.  It really needs a thorough overhaul.*

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

####**"has_borders="**
By default, individual pictures have a border.  For cartoons and similar fill-ins, it often
looks better without a border.  In that case, adding the has_borders attribute and setting it
to "False" (or "No") will remove the border.  


