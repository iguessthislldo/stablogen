import itertools
from .util import is_empty, has_method

class Page:
    # TODO: Possibly seperate the 'user' call  of __init__
    # (Page(iterable, size)) into a factory function

    # TODO: Create Direct Page Generator instead of generating the pages
    # all at once in the begining.
    def __init__(self, iterable, size, context=None):
        if context is None and iterable is not None and size is not None:
            # Special Case where I want there to be one page if the iterable
            # is empty. Else generate the regular pages.This replaced code
            # later in execution that made it appear that there was always
            # at least one page when there wasn't. 
            # (self.pages being [[]] vs [])
            if is_empty(iterable):  
                self.pages = [[]]
            else:
                self.pages = list(self.paginate(iterable, size))
            self.index = 0
            self.length = len(self.pages)
            self.per_page = size
        elif context is not None and iterable is None and size is None:
            self.pages = context['pages']
            self.index = context['index']
            self.length = context['length']
            self.per_page = context['per_page']
            if self.length <= self.index or self.index < 0:
                raise IndexError("Invalid Page context, page index is out of"
                                 "range")
        else:
            raise ValueError("Page() has two ways to init, Page(iterable,"
                             "size) XOR Page(None, None, context=context)")

    def get_pageno(self):
        return self.index + 1

    def get_items(self, index=None):
        if index is None:
            index = self.index
        return self.pages[index]

    def next(self):
        return self.index + 1

    def has_next(self):
        return self.index < (self.length - 1)

    def get_next(self):
        return self.__class__(None, None, context = dict(
            pages = self.pages,
            index = self.next(),
            length = self.length,
            per_page = self.per_page,
        ))

    def prev(self):
        return self.index - 1

    def has_prev(self):
        return self.index > 0

    def get_prev(self):
        return self.__class__(None, None, context = dict(
            pages = self.pages,
            index = self.prev(),
            length = self.length,
            per_page = self.per_page,
        ))

    @staticmethod
    def paginate(iterable, page_size):
        '''Break a iterable into "pages" of a certain size.
        Taken from http://stackoverflow.com/a/3744531
        '''
        while True:
            i1, i2 = itertools.tee(iterable)
            iterable, page = (itertools.islice(i1, page_size, None),
                    list(itertools.islice(i2, page_size)))
            if len(page) == 0:
                break
            yield page

    # Iteration methods
    def __iter__(self):
        return self

    def __getitem__(self, key):
        return self.get_items(key)

    def __next__(self):
        try:
            return self.get_next()
        except IndexError:
            raise StopIteration()

    # Humanization
    def __str__(self):
        return 'Page {} of {}'.format(self.get_pageno(), self.length)

    def __repr__(self):
        return '<{}: {}>'.format(self.__class__.__name__, str(self))

    def print(self):
        return str(self)

