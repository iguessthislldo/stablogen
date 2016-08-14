#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Python Standard Library
import os, sys
from pathlib import Path
import itertools
from urllib.parse import quote
from shutil import rmtree, copytree, copyfile

# 3rd Party Libraries
try:
    from jinja2 import Environment, FileSystemLoader, ChoiceLoader
    import arrow, yaml
except ImportError:
    sys.exit("One of the following is missing: jinja2, arrow, yaml\n" +
        "Try running: pip install Jinja2 arrow PyYAML" +
        "Also make sure you activated you virtual enviroment if your using one.")

# Local
from stablogen.util import if_none_else_do, make_url, to_list

# Paths
blog_dir = Path(__file__).resolve().parent
templates_dir = blog_dir / 'templates'
posts_dir = blog_dir / 'posts'
skl_dir = blog_dir / 'skl'
pages_dir = blog_dir / 'pages'
post_filename = 'post.yaml'
content_filename = 'content.html'
output_dir = blog_dir / 'output'

# Holds post data when acting on everyingthing
# (Listing things, generating, etc)
posts = dict()
all_tags = dict()

# Support Arrow Objects in PyYAML (At least date time equilvalent)
yaml.add_representer(arrow.Arrow, lambda dumper, data:
    dumper.represent_scalar('!arrow.Arrow', str(data))
)
yaml.add_constructor('!arrow.Arrow', lambda loader, node:
    arrow.get(loader.construct_scalar(node))
)

# Core code
class Post(yaml.YAMLObject):
    '''Core type of the program, represents a post in the blog.
    '''

    def __init__(
        self, title, content, tags=[], url=None, when=None,
        last_edited = None, created = None
    ):
        self.title = title
        self.url = make_url(title, url)
        self.content = content
        self.tags = tags
        self.when = when
        self.last_edited = last_edited
        self.created = created

    def create(self):
        self.create = arrow.utcnow()

    def finalize(self):
        self.when = arrow.utcnow()

    def edit(self):
        self.last_edited = arrow.utcnow()

    def apply_tags(self):
        for tag in self.tags:
            if tag in all_tags.keys():
                all_tags[tag].add_post(self)
            else:
                all_tags[tag] = Tag(tag, [self])

    def __str__(self):
        rest = (" " + self.when.humanize()) if self.when is not None else ""
        return self.title + ' (' + self.url + ')' + rest

    def __repr__(self):
        return '<' + self.__class__.__name__ + ': ' + str(self) + '>'

    # YAML type
    yaml_tag = '!blog.Post'

    @staticmethod
    def load(post_dir):
        if not post_dir.is_dir():
            return None
        post_file = post_dir / post_filename
        if not post_file.is_file():
            print(str(posts_dir) + ' doesn\'t have a "' + post_filename + '"')
            return None
        content_file = post_dir / content_filename
        if not content_file.is_file():
            print(str(posts_dir) + ' doesn\'t have a "' + content_filename + '"')
            return None

        # Get Post Meta data
        with post_file.open('r') as f:
            post = yaml.load(f)

        # Get Post Content
        with content_file.open('r') as f:
            post.content = f.read()

        if post.url != post_dir.name:
            print('WARNING: "' + post.url + '" does not match its directory name!')

        post.apply_tags()

        return post

    @classmethod
    def load_all(cls):
        for post_dir in posts_dir.glob('*'):
            post = cls.load(post_dir)
            if post is None:
                continue
            posts[post.url] = post

    def save(self):
        if not posts_dir.is_dir():
            posts_dir.mkdir()

        post_dir = posts_dir / self.url
        if not post_dir.is_dir():
            post_dir.mkdir()

        # Save Post Content
        content_file = post_dir / content_filename
        with content_file.open('w') as f:
            f.write(self.content)

        # Save Post Meta data
        content = self.content # Don't include content
        self.content = None
        post_file = post_dir / post_filename
        with post_file.open('w') as f:
            yaml.dump(self, f)
        self.content = content # Restore content

    @staticmethod
    def get_finalized(final=True):
        if final:
            is_final = lambda p: p.when is not None
        else:
            is_final = lambda p: p.when is None
        return filter(is_final, posts.values())

    def date(self):
        fmt = 'YYYY-MM-DD'
        when = "" if self.when is None else self.when.format(fmt)
        last_edited = "" if self.last_edited is None else " edited: " + self.when.format(fmt)
        return when + last_edited

class Tag:
    def __init__(self, name, posts=[]):
        self.name = name
        self.posts = posts

    def add_post(self, post):
        if post not in self.posts:
            self.posts.append(post)

# Subcommands
def generate():
    '''Using everything, generates the blog from page, templates, static and
    media files and the posts. Removes the output directory if it currently
    exists.
    '''
    # Remove output directory and copy skl directory
    if output_dir.is_dir():
        rmtree(str(output_dir))
    copytree(str(skl_dir), str(output_dir))

    def guess_autoescape(template_name):
        if template_name is None or '.' not in template_name:
            return False
        ext = template_name.rsplit('.', 1)[1]
        return ext in ('html', 'htm', 'xml')

    env = Environment(
        autoescape = guess_autoescape,
        loader = ChoiceLoader([
            FileSystemLoader(str(pages_dir)),
            FileSystemLoader(str(templates_dir)),
        ]),
        extensions = ['jinja2.ext.autoescape'],
        trim_blocks = True,
    )
    env.globals.update(dict(
        HOSTNAME = 'fred.hornsey.us',
        DISQUS_NAME = 'iguessthislldo',
        latest_posts = posts,
    ))

    for page in pages_dir.glob('*.html'):
        if page.name == 'index.html':
            page_dir = output_dir
        else:
            page_dir = output_dir / page.stem
            page_dir.mkdir()

        with (page_dir / 'index.html').open('w') as f:
            f.write(env.get_template(page.name).render())

    Post.load_all()
    posts_output_dir = output_dir / 'posts'
    posts_output_dir.mkdir()
    for url, post in posts.items():
        post_dir = posts_output_dir / url
        post_dir.mkdir()
        post_file = post_dir / 'index.html'
        with post_file.open('w') as f:
            f.write(env.get_template('post.html').render(post=post))

    with (posts_output_dir / 'index.html').open('w') as f:
        f.write(env.get_template('list_posts.html').render(
            posts = sorted(filter(
                lambda i: i.when is not None, posts.values()
                ), key=lambda p: p.when)
        ))
        
def new(title):
    '''Creates a empty post with a title supplied
    '''
    url = make_url(title)
    if (posts_dir / url).is_dir():
        sys.exit("{} is already a post".format(url))
    p = Post(title, "", url=url)
    p.create()
    p.save()

def finalized(url):
    post_dir = posts_dir / url 
    if not post_dir.is_dir():
        sys.exit("Not a valid post")
    p = Post.load(post_dir)
    p.finalize()
    p.save()

def edited(url):
    post_dir = posts_dir / url 
    if not post_dir.is_dir():
        sys.exit("Not a valid post")
    p = Post.load(post_dir)
    p.edit()
    p.save()

def list_tags():
    '''Sort them by decreasing number of posts they have, then secondarily
    alphabetically by name.
    '''
    Post.load_all()
    for tag in sorted(all_tags.values(),
        key = lambda tag: (-len(tag.posts), tag.name)
    ):
        print(tag.name, len(tag.posts))

def list_posts():
    Post.load_all()
    for post in sorted(posts.values(), key=lambda p: p.title):
        print(post)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required = True)
    group.add_argument('-g', '--generate', action='store_true')
    group.add_argument('-n', '--new',
        nargs = 1,
        metavar = 'TITLE',
    )
    group.add_argument('-f', '--finalized',
        nargs = 1,
        metavar = 'URL',
    )
    group.add_argument('-e', '--edited',
        nargs = 1,
        metavar = 'URL',
    )
    group.add_argument('-t', '--tags', action='store_true')
    group.add_argument('-p', '--posts', action='store_true')

    args = parser.parse_args()

    if args.generate:
        generate()
    elif args.new:
        new(args.new[0])
    elif args.finalized:
        finalized(args.finalized[0])
    elif args.edited:
        edited(args.edited[0])
    elif args.tags:
        list_tags()
    elif args.posts:
        list_posts()
    else:
        parser.print_help()

