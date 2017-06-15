import subprocess

from setuptools import setup
from setuptools.command.test import test as TestCommand


class TestSuite(TestCommand):
    user_options = []

    def initialize_options(self):
        TestCommand.initialize_options(self)

    def run_tests(self):
        subprocess.check_call(['docker-compose', 'build', 'test'])
        subprocess.check_call(['docker-compose', 'run', 'test'])


args = dict(
    name='aiobasex',
    version='0.0.1',
    description=' non-blocking client for BaseX, '
                'based on python/asyncio platform',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Development Status :: 4 - Beta',
        'Operating System :: POSIX',
        'Topic :: Database'
        'Topic :: Text Processing :: Markup :: XML',
        'Framework :: AsyncIO',
    ],
    author='Summer Babe',
    author_email='mksh@null.net',
    url='https://github.com/Intel471/prom-stats/',
    packages=['aiobasex'],
    license='MIT',
    cmdclass={'test': TestSuite},
)


setup(**args)
