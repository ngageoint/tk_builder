# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
from codecs import open

import os


# Get the long description from the README file
here = os.path.abspath(os.path.dirname(__file__))
# Get the long description from the README file
with open(os.path.join(here, 'README.md'), 'r') as f:
    long_description = f.read()


# Get the relevant setup parameters from the package
parameters = {}
with open(os.path.join(here, 'tk_builder', '__about__.py'), 'r') as f:
    exec(f.read(), parameters)


setup(name=parameters['__title__'],
      version=parameters['__version__'],
      description=parameters['__summary__'],
      long_description=long_description,
      long_description_content_type='text/markdown',
      packages=find_packages(exclude=('*tests*', '*example_apps*')),
      package_data={'tk_builder': ['*.xsd']},  # Schema files for SICD standard(s)
      url=parameters['__url__'],
      author=parameters['__author__'],
      author_email=parameters['__email__'],  # The primary POC
      install_requires=[
          'numpy', 'scipy', 'matplotlib', 'Pillow', 'sarpy>=1.2.36'],
      zip_safe=True,
      test_suite="tests",
      tests_require=[],
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: 3.8',
          'Programming Language :: Python :: 3.9'
      ],
      platforms=['any'],
      license='MIT'
      )
