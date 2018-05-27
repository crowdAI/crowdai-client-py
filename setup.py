from setuptools import setup


def find_requirements():
    with open("requirements.txt") as _in:
        required = [x.strip() for x in _in.read().splitlines()]
        return [x for x in required if x.strip() and not x.strip().startswith("#")]


setup(name='crowdai',
      version='1.0.22',
      description='Python client to interact with CrowdAI Grading Server.',
      url='https://github.com/spMohanty/crowdai-client-py',
      download_url='https://github.com/spMohanty/crowdai-client-py',
      author='S.P. Mohanty',
      author_email='sharada.mohanty@epfl.ch',
      license='GPLv3',
      packages=['crowdai', 'crowdai.challenges'],
      install_requires=find_requirements(),
      test_suite='nose.collector',
      tests_require=['nose'],
      zip_safe=False)
