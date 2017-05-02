from setuptools import setup

setup(name='crowdai',
      version='0.1',
      description='Python client to interact with CrowdAI Grading Server.',
      url='http://github.com/storborg/funniest',
      author='S.P. Mohanty',
      author_email='sharada.mohanty@epfl.ch',
      license='MIT',
      packages=['crowdai'],
      test_suite='nose.collector',
      tests_require=['nose'],
      zip_safe=False)
