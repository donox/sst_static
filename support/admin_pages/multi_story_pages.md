###Building Multi-Story Pages
<a id="#top"/>

####Index
[Story Snippet](#story-snippet)
[Intra-Page Navigation](#intra-page)

####Introduction
Pages containing more than one story are necessary for Page One and Page Two and any similar pages. In
Wordpress the pages were constructed manually by creating a (*very fragile*) HTML framework and cutting
and pasting content in it appropriately.  The HTML framework was complicated to follow, difficult to 
modify, and generally a maintenance nightmare.  

The goal here is to provide a more robust mechanism for creating the more complicated pages that does not
require the manipulation of HTML and is much more maintainable.  Unfortunately, multi-story pages have a
degree of intrinsic complexity that cannot be avoided without making them so rigid that they would often
not be suited to purpose.

The approach taken is to create a multi-story page by having a single file that describes the structure of 
the page with only a minimum of identification of the specific content.  Separately, each specific story
has an associated single file that provides the information needed to handle one story.  This allows stories
to be changed by replacing (or adding/deleting) individual stories without affecting other stories on 
the same page. The result is that a single multi-story page is managed as a file folder (or directory) 
containing one file for each story and one file for the page itself.

Each file in the folder is described with a widely used *"meta-language"* called **YAML** (Yet Another 
MetaLanguage).  A YAML file is basically a means of representing a nested list of items - much like 
the structure of a file directory or an outline. The formal definition of YAML can be found [here](
https://docs.ansible.com/ansible/latest/reference_appendices/YAMLSyntax.html); however, we use only
a small subset for our purposes.

The easiest way to build YAML files is to duplicate one of the example files such as 
[single story](/admin/example_single_entry.yaml) or
[structured page](/admin/example_multi_story_page.yaml) and modify it.  Things to 
note are the '---' at the beginning and the '...' at the end of the file.  Note the indenting to indicate
items at the same level and the use of the '- ' (does not occur in single entry file) to indicate a new
item in a list. There are a few other special characters that may conflict with our use.  There is a 
nice summary of the Gotchas [here](
https://docs.ansible.com/ansible/latest/reference_appendices/YAMLSyntax.html#gotchas).  In particular, a colon (:)
followed by a space or newline must be enclosed in quotes (generally use double quotes).

####Story Snippets
<a id="#story-snippet"/>
A story snippet is a short entry that can be placed on a multi-story page.  It may either be an entire
entry or it may be a teaser for a larger entry elsewhere and contain a **Read More** button linking to
the full story.  Use [this example](/admin/example_single_entry.yaml) to follow explanation. The
"---", "Entry", "entry_type", and "story" lines should be copied as is.

#####title, byline, photos
These entries are used to create the actual title, byline, and photo byline for the story.  Leave 
them blank (or remove them) if not needed.  Depending on the story, this may cause conflict with
things like an HTML title or byline included in the story and need to be accounted for (See
"starting_text" below.)

#####file_path
This is the location of the file in the page directory hierarchy for the site.  The top level
of the site is represented by the folder "pages/".  For example, the location of Page One would
be "pages/page-one.md".  Note also the (generally) ".md" extension associated with the file.

#####make_snippet
This is generally copied as is.  It is intended to handle the case (not yet implemented) where
the editors provide  separate specific snippet not taken from the file itself.

#####starting_text, stopping_text
This is used to select the portion of the file to be used as the snippet.  The system performs
a search for the starting_text (simple string search, EXACT match required).  That identifies
the beginning of the content to be used for the snippet.  If it is left blank, the content
begins at the start of the file.  This is often used to avoid things like titles or bylines that
are embedded in the document.

Similarly, the system searches for the stopping_text.  This is the first text that is NOT included
in the snippet.  Again, if it is left blank, the snippet continues to the end of the document.

There are a couple of issues that you need to be careful about. 
1. Be careful not to select text (starting_text is particularly bad) that happens to break an HTML 
   expression.  For example, if there is a "<div>Now is the time...</div>" and you want the text
   to begin with the "Now is...", be sure to include the initial "<div>" or the resulting page
   will have unbalanced structure.
2. Be careful with initial shortcodes.  It is often the case that the story includes a picture
   as the initial element which would imply that the starting text would begin "\{\{%singlepic...".
   This will fail as that creates invalid markdown.  The easiest way to avoid this is to insert
   a "<span/>" (an empty "span") element in the document before the shortcode and use that
   as the starting_text.  It generates nothing visible in the final document thus leaving the
   picture as the first thing as intended.
   
#####no_read_more
If the snippet is the entire content, use this to prevent the creation of a "Read More" button.

#####...
End the file with "..." on the beginning of a line.

####Intra-page Navigation
<a id="#story-snippet"/>

Intra-page navigation is supported for any entry.  There are two navigation elements available: **target** and
**goback**.  Note, they are placed in an entry at the same level as **entry-type** and are independent of one 
another.

#####target
**target** (note lower case) creates an *anchor* (HTML "a" tag) indicating the target to which the page may go.  All targets
accumulate during the building of the page and then displayed at the top of the page allowing the reader to 
click on any target and be taken directly to that story.

The text following the **target** is displayed to the user.  The navigation goes to the beginning of the containing 
**Entry**. 

#####goback
**goback** is placed after the defining entry, and the text is displayed to create the link.  The navigation takes 
the user back to the top of the page.  

[Back to Top](#top)




