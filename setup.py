'''
The setup.py file is a build script for setuptools, used to package and distribute Python projects. It typically contains metadata about the project, such as its name, version, author, and dependencies, as well as instructions on how to install the package.
'''
from setuptools import setup, find_packages
# find_packages will find src automatically then it will see whether it has __init__.py file or not if yes then it will consider that folder as package,then in that folder it will look for other packages like cloud,components,utils etc.
from typing import List


def get_requirements(file_path: str) -> List[str]:
    '''
    this function will return the list of requirements
    '''
    requirements = []
    with open(file_path) as file_obj:
        requirements = file_obj.readlines()
        requirements = [req.strip() for req in requirements]  # <-- FIX

        if '-e .' in requirements:
            requirements.remove('-e .')
  
    return requirements


setup(
    name='Network_Security',
    version='0.1.0',
    author='Danish Jain',
    author_email='danishsjain@gmail.com',
    packages =find_packages(),# finds src/ automatically
    install_requires=get_requirements('requirements.txt')
)