from setuptools import setup, find_packages
from codecs import open
from os import path

__version__ = '0.0.1'

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='little_r',
    version=__version__,
    description='Little_r format WRFDA tool',
    long_description=long_description,
    url='https://github.com/tommz9/python-little_r',
    license='BSD',
    classifiers=[
      'Development Status :: 3 - Alpha',
      'Intended Audience :: Developers',
      'Programming Language :: Python :: 3',
    ],
    keywords='',
    package_dir={'': 'src'},
    packages=['little_r'],
    include_package_data=True,
    author='Tomas Barton',
    install_requires=[
        'fortranformat',
        'click',
        'arrow'
    ],
    author_email='tommz9@gmail.com'
)
