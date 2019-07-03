import pytest
import sys
import os

from test_discovery import validate_yaml


def test_validate_yaml():
    """Check that the yaml validator runs. Also serves to check that all built in
    definitions.yaml are yaml."""
    directories_to_test = next(os.walk('examples'))[1]
    for directory_to_test in directories_to_test:
        discovery_directory = 'examples/{}'.format(directory_to_test)
        # will exit with 1 if yaml is not valid
        validate_yaml(discovery_directory)


if __name__ == '__main__':
    pytest.main(sys.argv)
