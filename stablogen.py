#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from stablogen.commands import *

if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
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

