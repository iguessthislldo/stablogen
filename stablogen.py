#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Python Standard Library
import os, sys
import re
from shutil import rmtree, copyfile

# 3rd Party Libraries
from jinja2 import Environment, PackageLoader, FileSystemLoader, ChoiceLoader
# pip install Jinja2 arrow PyYAML

# Local
from stablogen.config import *
from stablogen.Post import *

def setup_jinja(input_dir):
    def guess_autoescape(template_name):
        if template_name is None or '.' not in template_name:
            return False
        ext = template_name.rsplit('.', 1)[1]
        return ext in ('html', 'htm', 'xml')

    env = Environment(
        autoescape = guess_autoescape,
        loader = ChoiceLoader([
            FileSystemLoader(str(input_dir)), # Prefer input templates? (Hopefully)
            PackageLoader('stablogen'),
        ]),
        extensions = ['jinja2.ext.autoescape'],
        trim_blocks = True,
    )

    latest_posts = Post.get_finalized(input_dir)
    env.globals.update(dict(
        HOSTNAME = 'fred.hornsey.us',
        DISQUS_NAME = 'iguessthislldo',
        latest_posts = latest_posts,
        latest_post = latest_posts[0] if len(latest_posts) > 0 else None,
    ))

    return env

# Subcommands
def generate(input_dir, output_dir):
    '''Using everything, generates the blog from page, templates, static and
    media files and the posts. Removes the output directory if it currently
    exists.
    '''
    Post.load_all(input_dir)
    input_posts_dir = input_dir / posts_dirname
    templates_dir = input_dir / templates_dirname

    # Remove output directory if it exists
    if output_dir.is_dir():
        rmtree(str(output_dir))
    output_dir.mkdir()

    # Copy eveything in input to output as long as it's not to be
    # rendered or special

    def is_hidden(p):
        return re.match(r'^\..*$', p.name)

    def will_copy(p):
        return not any([
            p == input_posts_dir, # Will be generating posts later
            p == templates_dir, # Don't need to do anything else with
            is_hidden(p), # don't copy hidden things
            p.name == config_filename, # Don't copy config file
        ])

    dirs = []
    files = []

    # Get root directories and files we want to work with:
    for p in input_dir.glob('*'):
        if will_copy(p):
            (dirs if p.is_dir() else files).append(p)

    # Work recursively on choosen subdirectores (not hidden)
    for d in dirs:
        for p in d.glob('**/*'):
            if not is_hidden(p):
                (dirs if p.is_dir() else files).append(p)

    # Make Output Directories
    for p in dirs:
        (output_dir / p.relative_to(input_dir)).mkdir(
            parents=True,
            exist_ok=True
        )

    process_html = []

    # Handle Files
    for p in files:
        if p.suffix in RENDER_EXTENTIONS:
            process_html.append(p.relative_to(input_dir))
        elif p.is_file():
            copyfile(str(p), str(output_dir / p.relative_to(input_dir)))
        else:
            print('Input item "{}" was ignored').format(str(p))

    env = setup_jinja(input_dir)

    # Render Regular Pages
    for i in process_html:
        if i.name == 'index.html':
            page_dir = output_dir / i.parent
        else:
            page_dir = output_dir / i.parent / i.stem

        page_dir.mkdir(parents = True, exist_ok = True)
        (page_dir / 'index.html').write_text(env.get_template(str(i)).render())

    # Render Posts
    posts_output_dir = output_dir / posts_dirname
    posts_output_dir.mkdir()

    for url, post in Post.inventory.items():
        post_dir = posts_output_dir / url
        post_dir.mkdir()
        post_file = post_dir / 'index.html'
        with post_file.open('w') as f:
            f.write(env.get_template('post.html').render(post=post))

    # Render Posts Index
    with (posts_output_dir / 'index.html').open('w') as f:
        f.write(env.get_template('list_posts.html').render())

    # Render Tags
    tags_output_dir = output_dir / tags_dirname
    tags_output_dir.mkdir()

    for tag in Tag.inventory.values():
        tag_dir = tags_output_dir / tag.url
        tag_dir.mkdir()
        tag_file = tag_dir / 'index.html'
        with tag_file.open('w') as f:
            f.write(env.get_template('tag.html').render(tag=tag))

    # Render Tags Index
    with (tags_output_dir / 'index.html').open('w') as f:
        f.write(env.get_template('list_tags.html').render(
            tags=Tag.get_most_tagged(input_dir)
        ))

def new(input_dir, title):
    '''Creates a empty post with a title supplied
    '''
    url = make_url(title)
    post_dir = input_dir.joinpath(posts_dirname, url)
    if post_dir.is_dir():
        sys.exit("{} is already a post".format(url))
    p = Post(title, "", url=url)
    p.create()
    p.save(post_dir)

def finalized(input_dir, url):
    post_dir = input_dir.joinpath(posts_dirname, url)
    if not post_dir.is_dir():
        sys.exit("Not a valid post")
    p = Post.load(post_dir)
    p.finalize()
    p.save(post_dir)

def edited(input_dir, url):
    post_dir = input_dir.joinpath(posts_dirname, url)
    if not post_dir.is_dir():
        sys.exit("Not a valid post")
    p = Post.load(post_dir)
    p.edit()
    p.save(post_dir)

def list_tags(input_dir):
    '''Sort them by decreasing number of posts they have, then secondarily
    alphabetically by name.
    '''
    Post.load_all(input_dir)
    for tag in sorted(Tag.inventory.values(),
        key = lambda tag: (-len(tag.posts), tag.name)
    ):
        print(tag.name, len(tag.posts))

def list_posts(input_dir):
    Post.load_all(input_dir)
    for post in sorted(Post.inventory.values(), key=lambda p: p.title):
        print(post)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        '-g', '--generate',
        metavar = 'OUTPUT_DIR',
        nargs='?',
        action='append',
    )
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

    parser.add_argument('-i', '--input',
        metavar='INPUT_DIR',
        nargs='?',
    )

    args = parser.parse_args()

    if args.input is None:
        input_dir = Path('.') / default_input_dirname
    else:
        input_dir = Path(args.input)

    if args.generate is not None:
        if args.generate[0] is None:
            output_dir = Path('.') / default_output_dirname
        else:
            output_dir = Path(args.generate[0])
        generate(input_dir, output_dir)
    elif args.new:
        new(input_dir, args.new[0])
    elif args.finalized:
        finalized(input_dir, args.finalized[0])
    elif args.edited:
        edited(input_dir, args.edited[0])
    elif args.tags:
        list_tags(input_dir)
    elif args.posts:
        list_posts(input_dir)
    else:
        parser.print_help()

