from setuptools import setup, find_packages

setup(
	name='wlink',
	version='0.0.2',
	packages=find_packages('src/'),
	package_dir={'': 'src'},
	url='https://github.com/ostoic/wlink',
	license='GPLv3',
	author='Shaun Ostoic',
	author_email='ostoic@uwindsor.ca',
	description=''
)
