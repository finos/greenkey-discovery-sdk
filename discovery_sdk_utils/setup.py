from setuptools import setup

setup(
    name='discovery_sdk_utils',
    version='0.1.0',
    description='Contains useful functions for GreenKey Discovery',
    url='https://github.com/finos-voice/greenkey-discovery-sdk/discovery_sdk_utils',
    packages=['discovery_sdk_utils'],
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=[
        'pytest',
    ],
)
