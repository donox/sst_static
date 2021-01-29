### Building Multi-Story Pages

Pages containing more than one story are necessary for Page One and Page Two and any similar pages. In
Wordpress the pages were constructed manually by creating a (*very fragile*) HTML framework and cutting
and pasting content in it appropriately.  The HTML framework was complicated to follow, difficult to 
modify, and generally a maintenance nightmare.  

The goal here is to provide a more robust mechanism for creating the more complicated pages that does not
require the manipulation of HTML and is much more maintainable.  Unfortunately, multi-story pages have a
degree of intrinsic complexity that cannot be avoided without making them so rigid that they would often
not be suited to purpose.

The approach taken is to create a multi-story page by having a single file that describes the structure of 
the page with only a minimum on identification of the specific content.  Separately, each specific story
has an associated single file that provides the information needed to handle one story.  This allows stories
to be changed by replacing (or adding/deleting) individual stories without affecting other stories on 
the same page. The result is that a single multi-story page is managed as a file folder (or directory) 
containing one file for each story and one file for the page itself.

Each file in the folder is described with a widely used *"meta-language"* called **YAML** (Yet Another 
MetaLanguage).  A YAML file is basically a means of representing a nested list of items - much like 
the structure of a file directory or an outline. The formal definition of YAML can be found [here](
https://docs.ansible.com/ansible/latest/reference_appendices/YAMLSyntax.html); however, we use only
a small subset for our purposes.

The easiest way to build YAML files is to duplicate one of the example files and modify it.  Things to 
note are the '---' at the beginning and the '...' at the end of the file.  Note the indenting to indicate
items at the same level and the use of the '- ' (does not occur in single entry file) to indicate a new
item in a list. There are a few other special characters that may conflict with our use.  There is a 
nice summary of the Gotchas [here](
https://docs.ansible.com/ansible/latest/reference_appendices/YAMLSyntax.html#gotchas)

####Story Snippets
A story snippet is a short entry that can be placed on a multi-story page.  It may either be an entire
entry or it may be a teaser for a larger entry elsewhere and contain a **Read More** button linking to
the full story.


