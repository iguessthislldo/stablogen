#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Python Standard Library
import os, sys
import itertools
from urllib.parse import quote
from shutil import rmtree, copytree, copyfile

# 3rd Party Libraries
from jinja2 import Environment, FileSystemLoader, ChoiceLoader
# pip install Jinja2 arrow PyYAML

# Local
from stablogen.config import *
from stablogen.Post import *

# Subcommands
def generate():
    '''Using everything, generates the blog from page, templates, static and
    media files and the posts. Removes the output directory if it currently
    exists.
    '''
    Post.load_all()

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

    latest_posts = Post.get_finalized()
    env.globals.update(dict(
        HOSTNAME = 'fred.hornsey.us',
        DISQUS_NAME = 'iguessthislldo',
        latest_posts = latest_posts,
        latest_post = latest_posts[0] if len(latest_posts) > 0 else None,
    ))

    for page in pages_dir.glob('*.html'):
        if page.name == 'index.html':
            page_dir = output_dir
        else:
            page_dir = output_dir / page.stem
            page_dir.mkdir()

        with (page_dir / 'index.html').open('w') as f:
            f.write(env.get_template(page.name).render())

    posts_output_dir = output_dir / 'posts'
    posts_output_dir.mkdir()

    for url, post in Post.inventory.items():
        post_dir = posts_output_dir / url
        post_dir.mkdir()
        post_file = post_dir / 'index.html'
        with post_file.open('w') as f:
            f.write(env.get_template('post.html').render(post=post))

    with (posts_output_dir / 'index.html').open('w') as f:
        f.write(env.get_template('list_posts.html').render())

    tags_output_dir = output_dir / 'tags'
    tags_output_dir.mkdir()

    for tag in Tag.inventory.values():
        tag_dir = tags_output_dir / tag.url
        tag_dir.mkdir()
        tag_file = tag_dir / 'index.html'
        with tag_file.open('w') as f:
            f.write(env.get_template('tag.html').render(tag=tag))
        
    with (tags_output_dir / 'index.html').open('w') as f:
        f.write(env.get_template('list_tags.html').render(
            tags=Tag.get_most_tagged()
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
    for tag in sorted(Tag.inventory.values(),
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

