import logging
import os
import json
from os.path import abspath, exists, join as join_path
from testing.metrics import compute_all

logger = logging.getLogger(__name__)

TABLE_BAR_LENGTH = 160


def json_dump(data, outfile, directory=None):
    """
    :param data: json serializable object
    :param outfile: str; name of output file
    :param directory: str (optional);
    :return: saves data to file named outfile in directory (or current dir if unspecified)
    """
    if not directory:
        directory = os.getcwd()
    outfile = join_path(directory, outfile)
    json.dump(data, open(outfile, "w+"), indent=2)


def print_table(timing_list, top_n=5, first_k_chars=25):
    """ 
    Prints a formatted table ordered by longest test timings. 
        
    :param timing_list: namedtuple, list of namedtuples representing testing results
    """

    print(TABLE_BAR_LENGTH * '-')
    sorted_timing = sorted(
        timing_list, key=lambda tup: tup.time_dif_ms, reverse=True
    )
    print("\nTop", top_n, "longest timed tests:\n")
    print(
        '{:<30s}{:<12s}{:<30s}{:<35s}{:<25s}'.format(
            'test_file_name', 'test_no', 'test_name', 'transcript', 'time(ms)'
        )
    )
    print(TABLE_BAR_LENGTH * '-')

    for x in sorted_timing[:top_n]:
        print(
            '{:<30s}{:<12d}{:<30s}{:<35s}{:<25.2f}'.format(
                x.test_file[:first_k_chars], x.test_no,
                x.test_name[:first_k_chars], x.transcript[:first_k_chars],
                x.time_dif_ms
            )
        )

    print(TABLE_BAR_LENGTH * '-')


def print_failures(test_failures):
    """ 
    Prints a formatted table ordered by longest test timings. 
        
    :param timing_list: namedtuple, list of namedtuples representing testing results
    """

    table_string = '{:<40s}{:<20s}{:<50s}{:<50s}'

    print(TABLE_BAR_LENGTH * '-')
    print("\nTest failures:\n")
    print(
        table_string.format(
            'test_name', 'test_type', 'expected_value', 'observed_value'
        )
    )
    print(TABLE_BAR_LENGTH * '-')

    for t in test_failures:
        print(table_string.format(t[0][:40], t[1][:20], t[2][:50], t[3][:50]))

    print(TABLE_BAR_LENGTH * '-')


def record_results(output_dict, verbose=False, save_results=False):
    if verbose:
        logger.setLevel(logging.INFO)

    print("\n---\n")
    output_dir = os.path.dirname(output_dict["test_file"])

    if "total_characters" in output_dict and output_dict["total_characters"]:
        entity_character_error_rate = 100 * (
            output_dict["total_character_errors"] /
            output_dict["total_characters"]
        )
        logger.info(
            "Total number of entity character errors: {}".format(
                output_dict["total_entity_character_errors"]
            )
        )
        logger.info(
            "Entity Character Error Rate: {:.2f}".
            format(entity_character_error_rate)
        )

    # evaluate metrics; treat each possible intent as reference
    metrics_dict = compute_all(
        output_dict["expected_intents"], output_dict["observed_intents"]
    )

    # record message regardless of number of entity errors
    message = "\n({} / {}) tests passed in {} seconds from {}\n".format(
        output_dict["correct_tests"],
        output_dict["total_tests"],
        output_dict["test_time_sec"],
        output_dict["test_file"],
    )
    print(message)

    if save_results:
        os.makedirs('results', exist_ok=True)
        json_dump(
            data=output_dict,
            outfile="results/{}".format(
                output_dict["test_file"].split("/")[-1].replace(
                    ".txt", "_results.json"
                )
            )
        )
        json_dump(
            data=metrics_dict,
            outfile="results/{}".format(
                output_dict["test_file"].split("/")[-1].replace(
                    ".txt", "_metrics.json"
                )
            )
        )

    if output_dict["total_tests"] > output_dict["correct_tests"]:
        return False

    return True
