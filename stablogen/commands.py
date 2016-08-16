# Python Standard Library
import sys

# Local
from stablogen.generate import generate
from stablogen.config import *
from stablogen.Post import *

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

