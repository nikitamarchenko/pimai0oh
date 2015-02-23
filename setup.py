import uuid
from setuptools import setup, find_packages
from pip.req import parse_requirements


install_requires_pip = parse_requirements('requirements.txt',
                                          session=uuid.uuid1())


install_requires_setuptools = []

for ir in install_requires_pip:
    install_requires_setuptools.append(str(ir.req))

setup(
    name='pimai0oh',
    version='0.0.1',
    packages=find_packages(),
    url='',
    license='',
    author='',
    author_email='',
    description='',
    install_requires=install_requires_setuptools,
    setup_requires=["setuptools_git >= 0.3", ],
    include_package_data=True,
    zip_safe=False,
)
