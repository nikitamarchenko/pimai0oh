import uuid
from setuptools import setup, find_packages
from pip.req import parse_requirements


install_requires_pip = parse_requirements('requirements.txt',
                                          session=uuid.uuid1())

setup(
    name='pimai0oh',
    version='',
    packages=[''],
    url='',
    license='',
    author='',
    author_email='',
    description=''
)
