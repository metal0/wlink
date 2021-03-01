from setuptools import setup

setup(
	name='prowl.protocol',
	version='0.0.1',
	packages=[
		'prowl',
		'prowl.protocol', 'prowl.cryptography', 'prowl.utility',
		'prowl.protocol.auth', 'prowl.protocol.world',
		'prowl.protocol.auth.packets', 'prowl.protocol.world.packets'
	],
	package_dir={'': 'src'},
	url='https://github.com/ostoic/pont.protocol',
	license='GPLv3',
	author='Shaun Ostoic',
	author_email='ostoic@uwindsor.ca',
	description=''
)
