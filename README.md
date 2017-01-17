# stablogen

**stablogen** is [yet another](https://en.wikipedia.org/wiki/Yet_another) static
blog generator. It uses [Jinja](http://jinja.pocoo.org/) and
[Pygments](http://pygments.org/). If you want to make a real blog with a 
static blog generator, I **strongly** suggest you use one of the many others
that are eaiser to use, more powerful and/or have objectively better design
(e.g. As of writting [Jekyll](https://jekyllrb.com) or
[Pelican](http://blog.getpelican.com/) look good for just about anyone),
however I wrote this one and use it for
[my personal blog](https://fred.hornsey.us).

## Dependencies
To install the required dependencies, please run:
`pip install Jinja2 arrow PyYAML Pygments`. This is of course should be done
in a virtualenv.

## Usage
To generate a site: `./stablogen.py -g [OUTPUT] [INPUT]`

The when the program is generating the site, it takes a input directory and
creates a output. By default this is in the CWD and it will override the
output directory if it already exists. All other subcommands operate on the
input directory.

Everything in the input directory is copied exactly to the output except:
- HTML files in any (non-hidden) directory will be processed by Jinja and
copyied to a directory of the same name and location, named `index.html`.
- `posts` directory which will be processed like the HTML files, but the
content will be put in a Jinja template. Jinja renders the content before
putting it in the template so Jinja tags can be used inside the content.
- `templates` directory for extra templates.
- Hidden (dot) files and directories are ignored.
- `stablogen.yml` or `stablogen.yaml` in the root of input.

To create a post: `./stablogen.py -n TITLE [INPUT]`

It will inform you if the title's url slug conflicts with another post. Posts
are files with a meta section and a content section and are explained below.
They are placed in INPUT/posts ("input/posts" by default).

Ex: `./stablogen.py -n 'This is an Example Post'` -> `./input/posts/this_is_an_example_post.html`

Ex: `./stablogen.py -n 'This is Another Post' other_site` -> `./other_site/posts/this_is_an_example_post.html`

Posts have three internal timestamps, when the post was created (with the -n
option), then right before you intent to post it you can "finalize" it
by using the -f argument. Finally you can mark the post as being edited
by using the -e arguemnt. All these do it set the time and date shown in the
posts and what order they are displayed. The required URL for the -f and -e
arguments is the url slug of the post you want to change. Also the program will
accept the begining of the slug as long as it matches the begining of a single
post, else it will list the posts it matches so you can correct the command.

Ex:
```sh
$ ./stablogen.py -n 'This is an Example Post'
$ ./stablogen.py -n 'This is Another Post'
...
$ ./stablogen.py -e this_is
There are multiple posts starting with "this_is":
"input/posts/this_is_another_post.html"
"input/posts/this_is_an_example_post.html"
$ ./stablogen.py -e this_is_another
$
```


## Post Format
```
title: This is a Title
url: this_is_a_title
tags: [tag1, "This is a tag with spaces"]
created: !arrow.Arrow '1970-01-01T00:00:00+00:00'
when: null
last_edited: null

<p>This is content.</p>
```

I googled my first choice for a project name, it turned out someone else had
thought of it: [alexex/blogen](https://github.com/alexex/blogen). I decided to
change the name to "stablogen" but I ~~stole~~ borrowed their format for
posts. I had them in two seperate files which was easier to program but not
as elegant. The only differecne real difference is that I'm using just HTML
and alexex is using Markdown for post content, which I might make possible
someday as an option.

The format is the post meta information in [YAML](http://yaml.org), followed
by **a blank line**, then the HTML of the post content. The YAML can be read
in any order, but I am forcing it to be output in the order above everytime
for readability. When changing it, it would be good to know at least the
basics of [YAML](https://learnxinyminutes.com/docs/yaml). You can put what
ever you want in the beggining as long as it's valid YAML, there's no blank
line before before the content begins, and all the required tags are there.

