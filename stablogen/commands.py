# Python Standard Library
import sys

# Local
from stablogen.generate import generate
from stablogen.config import *
from stablogen.Post import *
from stablogen.util import find_files

def new(input_dir, title):
    '''Creates a empty post with a title supplied
    '''
    url = make_url(title)
    posts_dir = input_dir / posts_dirname
    preexisting = find_files(posts_dir, url, post_file_exts, False)
    if preexisting:
        sys.exit('Result URL Slug: "{}" is already taken by:\n{}'.format(
            url, '\n'.join(map(lambda i: '"{}"'.format(i), preexisting))
        ))
    p = Post(title, "", url=url, extension = post_file_exts[0])
    p.create()
    p.save(posts_dir)

# Not a command, helper for finalized and edited
def check_for_multiple(posts_dir, url):
    files = find_files(posts_dir, url, post_file_exts, False)
    n = len(files)
    if n > 1:
        sys.exit('There are multiple posts starting with "{}":\n{}'.format(
            url, '\n'.join(map(lambda i: '"{}"'.format(i), files))
        ))
    elif n == 0:
        sys.exit("No post url slug starting with that name")
    return Post.load(files[0])

def finalized(input_dir, url):
    posts_dir = input_dir / posts_dirname
    p = check_for_multiple(posts_dir, url)
    p.finalize()
    p.save(posts_dir)

def edited(input_dir, url):
    posts_dir = input_dir / posts_dirname
    p = check_for_multiple(posts_dir, url)
    p.edit()
    p.save(posts_dir)

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
    for post in sorted(
        Post.inventory.values(),
        key=lambda p: p.created,
        reverse = True
    ):
        print(post)

