from setuptools import setup

setup(
	name='wlink',
	version='0.0.1',
	packages=[
		'wlink',
		'wlink.protocol', 'wlink.cryptography', 'wlink.utility',
		'wlink.protocol.auth', 'wlink.protocol.world',
		'wlink.protocol.auth.packets', 'wlink.protocol.world.packets'
	],
	package_dir={'': 'src'},
	url='https://github.com/ostoic/prowl',
	license='GPLv3',
	author='Shaun Ostoic',
	author_email='ostoic@uwindsor.ca',
	description=''
)
