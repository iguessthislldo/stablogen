from .Page import Page

import unittest

class Page_Tests(unittest.TestCase):
    def test_multiple_pages(self):
        test_data = [1, 2, 3, 4, 5, 6, 7, 8, 9]

        p1 = Page(test_data, 4)
        self.assertFalse(p1.has_prev())
        self.assertTrue(p1.has_next())
        self.assertTrue(p1.get_pageno() == 1)
        self.assertTrue(p1.get_items() == [1, 2, 3, 4])

        self.assertRaises(IndexError, lambda: p1.get_prev())

        p2 = p1.get_next()
        self.assertTrue(p2.has_prev())
        self.assertTrue(p2.has_next())
        self.assertTrue(p2.get_pageno() == 2)
        self.assertTrue(p2.get_items() == [5, 6, 7, 8])

        p3 = p2.get_next()
        self.assertTrue(p3.has_prev())
        self.assertFalse(p3.has_next())
        self.assertTrue(p3.get_pageno() == 3)
        self.assertTrue(p3.get_items() == [9])

        self.assertRaises(IndexError, lambda: p3.get_next())

        p2 = p3.get_prev()
        self.assertTrue(p2.has_prev())
        self.assertTrue(p2.has_next())
        self.assertTrue(p2.get_pageno() == 2)
        self.assertTrue(p2.get_items() == [5, 6, 7, 8])

    def test_empty_iterable(self):
        p = Page([], 1)
        self.assertFalse(p.has_next())
        self.assertFalse(p.has_prev())
        self.assertTrue(p.get_pageno() == 1)
        self.assertTrue(p.get_items() == [])
        self.assertTrue(p.length == 1)
