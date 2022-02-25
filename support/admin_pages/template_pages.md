#User Guide to Building Pages Using Templates
This user guide the process and mechanics for creating pages that are rendered by a pre-defined template.
The creation of the template requires a developer, but is not a significant barrier when a new template
is useful for creating/defining a new type of page.

The initial use of the  capability is to render the Sunnybear stories that require control over positioning
and placement of text and pictures, but follow are well-defined pattern.

The creation of a template-based story requires adding parameters to the story's meta.txt file and creating
a **xxstoryxx.txt** file (substitute the story name for the 'xxstoryxx') specifying the elements that the system
will need to properly fill in the template.  

The story file is formally a **<a href="https://www.tutorialspoint.com/yaml/yaml_basics.htm">YAML</a>** file, 
though we only use a small part of the capabilities.  Using a formal language to specify the content allows
us to take advantage of many support tools for reading, checking, parsing, etc.

In creating the file, the syntactic elements to watch for include:
1. The '---' is a separator for each group of content.
2. Attributes that correspond to template content are at the start of a line and followed by a ": " (colon and space)
3. A list of items providing the content are on separate lines, indented equally with an initial "- " (dash and space)
4. Quote marks surrounding an item an *not* part of the content and indicate that the enclosed text is to be taken
without interpretation.  (Note for example the occurrence of the ": " inside the quote marks.)
5. Do not use tabs - use spaces to position elements.

There are other things that can be done, if we find that the need arises.

###Sunnybear Template 
The normal Sunnybear story (side-by-side photos and text, alternating sides) can be completed using a template. 
All that is required is to provide the photos and a file giving the values to be substituted in the template.
An example of a Sunnybear story file can be 
downloaded <a href="/files/downloads/admin/Sunnybear_New_Year.txt" download="sunny">here</a>.

Each '---' defines a different *section* of the file.  Except for the first section, each section corresponds
to a single photo and associated text.

The first section has the title and byline.  After that, there are four sections each with a picture and one
or more comments by Momabear or Babybear.  Pictures and content will alternate positions as they flow
down the page.

