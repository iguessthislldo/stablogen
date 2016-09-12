# Python Standard Library
import re
from shutil import rmtree, copyfile

# 3rd Party Libraries
from jinja2 import Environment, PackageLoader, FileSystemLoader, ChoiceLoader

# Local
from stablogen.config import *
from stablogen.Post import *
from stablogen.code import CodeExtension, output_code_style

def setup_jinja(input_dir):
    def guess_autoescape(template_name):
        if template_name is None or '.' not in template_name:
            return False
        ext = template_name.rsplit('.', 1)[1]
        return ext in ('html', 'htm', 'xml')

    env = Environment(
        autoescape = False,
        loader = ChoiceLoader([
            FileSystemLoader(str(input_dir)), # Prefer input templates? (Hopefully)
            PackageLoader('stablogen'),
        ]),
        extensions = [
            'jinja2.ext.autoescape',
            CodeExtension,
        ],
        trim_blocks = True,
    )

    latest_posts = Post.get_finalized(input_dir)
    env.globals.update(dict(
        HOSTNAME = 'https://fred.hornsey.us',
        DISQUS_NAME = 'iguessthislldo',
        latest_posts = latest_posts,
        latest_post = latest_posts[0] if len(latest_posts) > 0 else None,
    ))

    return env

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

    # Render Post content
    for post in Post.inventory.values():
        post.content = env.from_string(post.content).render()

    # Render Regular Pages
    for i in process_html:
        if i.name == 'index.html':
            page_dir = output_dir / i.parent
        else:
            page_dir = output_dir / i.parent / i.stem

        page_dir.mkdir(parents = True, exist_ok = True)
        (page_dir / 'index.html').write_text(env.get_template(str(i)).render())

    # Render Actual Post Pages
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

    # Codehighlighting css
    output_code_style(output_dir / PYGMENTS_CSS_OUTPUT)

