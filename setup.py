from distutils.core import setup

import mplchaco

setup(
    name='mplchaco',
    version=mplchaco.__version__,
    packages=['mplchaco'],
    author=mplchaco.__author__,
    author_email='aka.tkf@gmail.com',
    license=mplchaco.__license__,
    long_description=mplchaco.__doc__,
    classifiers=[
        "Development Status :: 3 - Alpha",
        # see: http://pypi.python.org/pypi?%3Aaction=list_classifiers
        ],
)
