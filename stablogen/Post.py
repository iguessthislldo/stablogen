# Python Standard Library
from collections import OrderedDict
import itertools

# 3rd Party Libraries
import arrow, yaml

# Local
from stablogen.config import *
from stablogen.util import make_url, find_files

# Uses OrderedDict to keep order the data in the order below
yaml.add_representer(OrderedDict, lambda self, data:
    self.represent_mapping('tag:yaml.org,2002:map', data.items())
)
post_yaml_tags = ('title', 'tags', 'created', 'when', 'last_edited')

# Support Arrow Objects in PyYAML (At least date time equilvalent)
arrow_tag='!arrow.Arrow'
yaml.add_representer(arrow.Arrow, lambda dumper, data:
    dumper.represent_scalar(arrow_tag, str(data))
)
yaml.add_constructor(arrow_tag, lambda loader, node:
    arrow.get(loader.construct_scalar(node))
)

# Core code
class Post:
    '''Core type of the program, represents a post in the blog.
    '''
    inventory = dict()
    loaded = False

    def __init__(
        self, title, content, tags=[], url=None, when=None,
        last_edited = None, created = None, extension = None
    ):
        self.title = title
        self.url = make_url(title, url)
        self.content = content
        self.tags = tags
        self.when = when
        self.last_edited = last_edited
        self.created = created
        self.extension = extension

    def create(self):
        self.created = arrow.utcnow()

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

    @staticmethod
    def load(post_file):
        if not post_file.is_file():
            return None
        
        lines = iter(post_file.read_text().split('\n'))
        m = yaml.load('\n'.join(itertools.takewhile(str.strip, lines)))
        return Post(
            title = m['title'],
            tags = m['tags'],
            content = '\n'.join(lines),
            created = m['created'],
            when = m['when'],
            last_edited = m['last_edited'],
            extension = post_file.suffix,
        )

    @classmethod
    def load_all(cls, input_dir):
        if not cls.loaded:
            for post_file in find_files(
                input_dir/posts_dirname,
                exts = post_file_exts
            ):
                post = cls.load(post_file)
                if post is None:
                    continue
                post.apply_tags()
                Post.inventory[post.url] = post
            cls.loaded = True

    def save(self, posts_dir):
        if not posts_dir.is_dir():
            posts_dir.mkdir(parents=True, exist_ok=True)

        ordered = OrderedDict()
        for tag in post_yaml_tags:
            ordered[tag] = getattr(self, tag)
        posts_dir.joinpath(self.url + self.extension).write_text(
            yaml.dump(ordered) + '\n' + self.content
        )

    @classmethod
    def get_finalized(cls, input_dir, final=True):
        cls.load_all(input_dir)
        if final:
            is_final = lambda p: p.when is not None
        else:
            is_final = lambda p: p.when is None
        return sorted(
            filter(is_final, cls.inventory.values()),
            key=lambda p: p.when,
            reverse=True
        )

    def date(self, fmt = 'YYYY-MM-DD'):
        when = "" if self.when is None else self.when.format(fmt)
        last_edited = "" if self.last_edited is None else (
            " edited: " + self.when.format(fmt)
        )
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
    def get_most_tagged(cls, input_dir):
        Post.load_all(input_dir)
        return sorted(
            cls.inventory.values(),
            key = lambda t: len(t.posts),
            reverse = True
        )

