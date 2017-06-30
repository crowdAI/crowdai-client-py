from setuptools import setup
from collections import defaultdict
from pip.req import parse_requirements

setup(name='crowdai',
      version='1.0.4',
      description='Python client to interact with CrowdAI Grading Server.',
      url='https://github.com/spMohanty/crowdai-client-py',
      download_url='https://github.com/spMohanty/crowdai-client-py',
      author='S.P. Mohanty',
      author_email='sharada.mohanty@epfl.ch',
      license='GPLv3',
      packages=['crowdai', 'crowdai.challenges'],
      install_requires=[
          'appdirs>=1.4.3',
          'click>=6.7',
          'enum-compat>=0.0.2',
          'enum34>=1.1.6',
          'Flask>=0.12.1',
          'itsdangerous>=0.24',
          'Jinja2>=2.9.6',
          'MarkupSafe>=1.0',
          'packaging>=16.8',
          'pyparsing>=2.2.0',
          'requests>=2.14.1',
          'six>=1.10.0',
          'socketIO-client-2>=0.7.4',
          'termcolor>=1.1.0',
          'tqdm>=4.11.2',
          'websocket-client>=0.40.0',
          'Werkzeug>=0.12.1'
      ],
      test_suite='nose.collector',
      tests_require=['nose'],
      zip_safe=False)
