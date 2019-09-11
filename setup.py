from setuptools import setup

setup(name='deaglefootball',
      version='0.1',
      description='Fantasy Football Auto Pilot',
      url='http://github.com/bryandeagle/football',
      author='Bryan Deagle',
      author_email='bryan@dea.gl',
      license='MIT',
      packages=['deaglefootball'],
      install_requires=[
          'ff-espn-api',
          'requests',
          'jinja2',
          'pyyaml',
          'bs4'],
      zip_safe=False)
