from setuptools import setup, find_packages

classifiers = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'Operating System :: OS Independent',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3'
]

setup(
    name='TwitterScraperAPI',
    version='1.0.10',
    description='Library for getting twitter data',
    long_description=open('README.md').read() + '\n\n' + open('CHANGELOG.txt').read(),
    url='https://github.com/vaskrneup/TwitterScraperAPI',
    author='Bhaskar Neupane',
    author_email='bhaskar.neupane.58@gmail.com',
    license='MIT',
    classifiers=classifiers,
    keywords='twitter scraper',
    packages=find_packages(),
    install_requires=['beautifulsoup4', 'requests']
)
