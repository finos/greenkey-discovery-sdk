import pytest
import sys
import os

from test_discovery import validate_entities, validate_json

def test_validate_entities(capsys):
    """Check that the entity validator runs. Also serves to check that all built in
    entity definitions are valid."""
    directories_to_test = next(os.walk('examples'))[1]
    for directory_to_test in directories_to_test:
        discovery_directory = 'examples/{}'.format(directory_to_test)

        validate_entities(discovery_directory)
        captured = capsys.readouterr()
        try:
            output = captured.out # works for newer python versions of pytest
        except AttributeError:
            output = captured[0] # works for python 3.4 and older versions of pytest
        print(output)
        assert output.endswith("No errors!\n")

def test_validate_json(capsys):
    """Check that the json validator runs. Also serves to check that all built in
    intents.json are json."""
    directories_to_test = next(os.walk('examples'))[1]
    for directory_to_test in directories_to_test:
        discovery_directory = 'examples/{}'.format(directory_to_test)
        # will exit with 1 if json is not valid
        validate_json(discovery_directory)


if __name__ == '__main__':
    pytest.main(sys.argv)
