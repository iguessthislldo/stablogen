#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Python Standard Library
import os, sys
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.parse import quote
import operator

# 3rd Party Libraries
from jinja2 import Environment, FileSystemLoader
import arrow import yaml

# Paths
blog_dir = Path(__file__).resolve().parent
templates_dir = blog_dir / 'templates'
posts_dir = blog_dir / 'posts'
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

# Utility Functions
def editor(init_message=""):
    '''
    Open temporary file in program defined by EDITOR enviromental
    variable (defaults to "vi"), once the program is done, return the file
    as a string.
    '''
    with TemporaryDirectory() as tmp_dir:
        tmp_file = Path(tmp_dir) / 'post'
        with tmp_file.open('w') as f:
            f.write(init_message)

        os.system('%s %s' % (os.getenv('EDITOR', 'vi'), str(tmp_file)))

        with tmp_file.open('r') as f:
            result = f.read()

    return result

def if_none_else_do(val, func):
    ''' Return None if value is none, else return func(val) '''
    return None if val is None else func(val)

def make_url(title, url = None):
    if url is None:
        return quote(title.lower().replace(' ', '_'))
    else:
        return url

def to_list(val: str):
    return list(map(str.strip, val.split(',')))

# Core code
class Post(yaml.YAMLObject):
    def __init__(
        self, title, content, tags=[], url=None, when=None,
        last_edited = None
    ):
        self.title = title
        self.url = make_url(title, url)
        self.content = content
        self.tags = tags
        self.when = when
        self.last_edited = last_edited

    def finalize(self):
        self.when = arrow.utcnow()

    def apply_tags(self):
        for tag in self.tags:
            if tag in all_tags.keys():
                all_tags[tag].add_post(self)
            else:
                all_tags[tag] = Tag(tag, [self])


    def __str__(self):
        return self.title + ' (' + self.url + '): ' + self.when.humanize()

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
        print('Saving Post: "' + self.title + '"...')

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

class Tag:
    def __init__(self, name, posts=[]):
        self.name = name
        self.posts = posts

    def add_post(self, post):
        if post not in self.posts:
            self.posts.append(post)

# Subcommands
def generate():
    if output_dir.is_dir():
        l = list(output_dir.rglob(''))
        for i in reversed(l):
            if i.is_file():
                i.unlink()
            else:
                i.rmdir()
    output_dir.mkdir()

    def guess_autoescape(template_name):
        if template_name is None or '.' not in template_name:
            return False
        ext = template_name.rsplit('.', 1)[1]
        return ext in ('html', 'htm', 'xml')

    env = Environment(
        autoescape = guess_autoescape,
        loader = FileSystemLoader(str(templates_dir)),
        extensions = ['jinja2.ext.autoescape'],
        trim_blocks = True,
    )

    with (output_dir / 'index.html').open('w') as f:
        f.write(env.get_template('index.html').render(latest_posts=[]))

    Post.load_all()
    posts_output_dir = output_dir / 'posts'
    for post in posts:
        post_dir = posts_output_dir / post.url
        post_dir.mkdir()
        post_file = post_dir / 'index.html'
        with post_file.open('w') as f:
            f.write(env.get_template('post.html').render(post=post))
        

def post():
    title = input("What to call this post?")
    tags = to_list(input("What to tag it? (Seperate tags with ',')"))
    content = editor()
    if content == "":
        sys.exit("Blank post content")
    Post(title, content, tags).save()

def edit():
    pass

def list_tags():
    '''
    Sort them by decreasing number of posts they have, then secondarily
    alphabetically by name.
    '''
    Post.load_all()
    for tag in sorted(all_tags.values(),
        key = lambda tag: (-len(tag.posts), tag.name)
    ):
        print(tag.name, len(tag.posts))

def list_posts():
    Post.load_all()
    print(posts)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'what',
        choices=[
            'generate',
            'post',
            'edit',
            'list-tags',
            'list-posts',
        ]
    )

    cmd = parser.parse_args().what

    if cmd == 'generate':
        generate()
    elif cmd == 'post':
        post()
    elif cmd == 'edit':
        edit()
    elif cmd == 'list-tags':
        list_tags()
    elif cmd == 'list-posts':
        list_posts()

