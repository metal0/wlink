from setuptools import setup

setup(
	name='wlink',
	version='0.0.2',
	packages=[
		'wlink',
		'wlink.cryptography', 'wlink.utility',
		'wlink.auth', 'wlink.world',
		'wlink.auth.packets', 'wlink.world.packets'
	],

	package_dir={'': 'src'},
	url='https://github.com/ostoic/wlink',
	license='GPLv3',
	author='Shaun Ostoic',
	author_email='ostoic@uwindsor.ca',
	description=''
)
