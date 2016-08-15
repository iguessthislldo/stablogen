import arrow, yaml

from stablogen.config import *
from stablogen.util import make_url

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
    inventory = dict()
    loaded = False

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
            if tag in Tag.inventory.keys():
                Tag.inventory[tag].add_post(self)
            else:
                Tag.inventory[tag] = Tag(tag, [self])

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
        if not cls.loaded:
            for post_dir in posts_dir.glob('*'):
                post = cls.load(post_dir)
                if post is None:
                    continue
                Post.inventory[post.url] = post
            cls.loaded = True

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

    @classmethod
    def get_finalized(cls, final=True):
        cls.load_all()
        if final:
            is_final = lambda p: p.when is not None
        else:
            is_final = lambda p: p.when is None
        return sorted(
            filter(is_final, cls.inventory.values()),
            key=lambda p: p.when
        )

    def date(self, fmt = 'YYYY-MM-DD'):
        when = "" if self.when is None else self.when.format(fmt)
        last_edited = "" if self.last_edited is None else " edited: " + self.when.format(fmt)
        return when + last_edited

class Tag:
    inventory = dict()

    def __init__(self, name, posts=[]):
        self.name = name
        self.url = make_url(name)
        self.posts = posts

    def add_post(self, post):
        if post not in self.posts:
            self.posts.append(post)

    @classmethod
    def get_most_tagged(cls):
        Post.load_all()
        return sorted(
            cls.inventory.values(),
            key = lambda t: len(t.posts),
            reverse = True
        )
