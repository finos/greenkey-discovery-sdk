from setuptools import setup

setup(
    name='gk_cli',
    version='0.1.1',
    packages=['gk_cli'],
    install_requires=['PyInquirer'],
    entry_points={
        'console_scripts': [
            'gk_cli = gk_cli.__main__:main'
        ]
    })
