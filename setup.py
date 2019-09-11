from setuptools import setup

setup(name='football',
      version='0.1',
      description='Fantasy football automations',
      url='http://github.com/bryandeagle/football-autopilot',
      author='Bryan Deagle',
      author_email='bryan@dea.gl',
      license='MIT',
      packages=['football'],
      install_requires=[
          'ff-espn-api',
          'requests',
          'jinja2',
          'pyyaml',
          'bs4'],
      zip_safe=False)
