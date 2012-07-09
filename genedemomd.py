#!/usr/bin/env python

"""
Generate a markdown file to view demos.
"""

from mplchaco.demo import demos


def genedemomd(path, root, ext):
    file(path, "w").write(generate_markdown(root, ext))


def generate_markdown(root, ext):
    mplpath = "/".join(([root] if root else []) + ["mpl"])
    chacopath = "/".join(([root] if root else []) + ["chaco"])
    imgfmt = "![{0} {{0}}]({1}/{{0}}.{2})".format
    geneimage = "\n".join([
        imgfmt("matplotlib", mplpath, ext),
        imgfmt("Chaco", chacopath, ext),
    ]).format

    lines = [geneimage(f.__name__) for f in demos]
    return "\n\n".join(lines)


def main():
    from argparse import ArgumentParser
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('path')
    parser.add_argument('--ext', default="png")
    parser.add_argument(
        '--root',
        default="https://github.com/tkf/mplchaco/raw/data")
    args = parser.parse_args()
    genedemomd(**vars(args))


if __name__ == '__main__':
    main()
