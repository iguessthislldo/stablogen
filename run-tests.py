#!/usr/bin/env python3
# -*- coding: utf-8 -*-

if __name__ == '__main__':
    import unittest
    from pathlib import Path
    tests = unittest.TestLoader().discover(
        str(Path(__file__).parent / 'stablogen')
    )
    unittest.TextTestRunner(verbosity=1).run(tests)
