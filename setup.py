from setuptools import setup, find_packages
import os

version = '1.0'

setup(name='pymassmailer',
      version=version,
      description="Mass Mailer using mallow mailer and jinja2 templates",
      long_description=open("README.md").read() + "\n" +
                       open(os.path.join("docs", "TODO.txt")).read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: Apache Software License"
        ],
      keywords='EMAIL SMTP JINJA',
      author='Matthew Levandowski',
      author_email='levandowski.matthew@gmail.com',
      url='https://github.com/hur1can3/pymassmailer',
      license='Apache',
      packages=find_packages(exclude=['ez_setup']),
      include_package_data=True,
      package_data = {
        # If any package contains *.csv or *.rst files, include them:
        '': ['*.csv', '*.rst'],
      },
      zip_safe=False,
      install_requires=[
          'marrow.mailer',
          'jinja2'
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
