from setuptools import setup
from collections import defaultdict
from pip.req import parse_requirements

requirements = []
extras = defaultdict(list)
for r in parse_requirements('requirements.txt', session='hack'):
    if r.markers:
        extras[':' + str(r.markers)].append(str(r.req))
    else:
        requirements.append(str(r.req))


setup(name='crowdai',
      version='0.1',
      description='Python client to interact with CrowdAI Grading Server.',
      url='http://github.com/storborg/funniest',
      author='S.P. Mohanty',
      author_email='sharada.mohanty@epfl.ch',
      license='MIT',
      packages=['crowdai', 'crowdai.challenges'],
      install_requires=requirements,
      extras_require=extras,
      test_suite='nose.collector',
      tests_require=['nose'],
      zip_safe=False)
