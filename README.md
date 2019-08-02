# GreenKey Scribe Discovery SDK [![Build Status](https://travis-ci.org/finos/greenkey-discovery-sdk.svg?branch=master)](https://travis-ci.org/finos/greenkey-discovery-sdk)
> Speed up business workflows through creating custom 'voice skills' and text interpreters

<img src="https://greenkeytech.com/wp-content/uploads/2019/02/gk_logo_colorlight.png" width="300" />

---

The Discovery SDK allows you to write logic-based interpreters, and let Scribe's Discovery engine use probabilistic search to identify intents and entities.

You can use your Discovery interpreter to power several voice-driven workflows such as:

- Building a skill in combination with [Scribe's Real-Time Dictation](https://transcription.greenkeytech.com/sqc-06437d7/)

- Searching transcribed files for key phrases with [Scribe's File Transcription](https://transcription.greenkeytech.com/svt-e0286da/)

Read more about Discovery on our [blog](https://greenkeytech.com/greenkey-scribe-discovery-skills/) or [checkout the full documentation](https://transcription.greenkeytech.com/discovery-1890af/)

The GreenKey Discovery SDK
is hosted by the [Voice Program] of the Fintech Open Source Foundation ([FINOS]).
If you are a company interested in the evolution of
open standards, interoperability, and innovation in the financial services sector,
please consider joining FINOS.

# Overview
1. [Quickstart](#1-quickstart)
    - Step through the 'digit' interpreter example.

2. [Customization and Discovery CLI](#2-customization-and-discovery-cli)
    - Customize your own interpreter and use the Discovery CLI to set up a project or entities.

3. [Advanced Examples and Documentation](#3-advanced-examples-and-documentation)
    - Transcribing voice audio files with SVTServer and using the Discovery engine.


# 1. Quickstart

## Requirements

- Docker 17+ (or Discovery Binaries)
- Python 3 with `pip`

## Dependencies

To ensure your dependencies install correctly, we recommend that you upgrade your `setuptools` before proceeding further.

```sh
python3 -m pip install --upgrade setuptools
```

Now you are ready to install the required dependencies with `pip`.
This will provide you with the packages needed to run the `test_discovery.py` script (see the 'digit' example below), as well as the Discovery CLI.

```sh
python3 -m pip install -r requirements.txt
```

## Using Compiled Binary Files

If you are unable to use Docker, contact us to obtain compiled binary files for Discovery.
Simply place the binaries directory into the SDK directory before running `test_discovery.py`.
The test script will automatically detect the binaries directory and use that instead of a Docker image.

Make sure not to change the name of the binaries file when you move it.
You should end up with a structure like the following for the `test_discovery.py` script to work.

```
└───greenkey-discovery-sdk
    └───discovery_binaries_windows_10_64bit__python37_64bit
    └───examples
    └───gk_cli
    │   discovery_config.py
    │   README.md
    │   test_discovery.py
```

## Obtaining Credentials
[Contact us](mailto:transcription@greenkeytech.com) to obtain credentials to obtain the Discovery Docker container from our repository and launch the Discovery engine.


## Discovery Examples Directory Overview
Each discovery example contains a folder named `custom`, which in turn contains the required `definitions.yaml` file.
Some examples contain a `schemas` key in the `definitions.yaml` file to customize the return json.
They also contain example scripts to see how the particular configuration will detect entities.

```
examples
└── digit
    ├── custom
    │   └── definitions.yaml
    ├── send_transcript_to_discovery.sh
    └── tests.txt
```


## The 'digit' Interpreter Example

1) Test cases for the room dialing example are in `examples/digit/tests.txt`
    ```
    intent_whitelist: digit

    test: dial number
    transcript: please dial eight
    room_number: 8

    test: dial number
    transcript: press one eight
    room_number: 1
    ...
    ```

    `tests.txt` follows the following format:
    ```
    # Comments are ignored
    test: {name of test}
    transcript: {transcript you want to parse}
    {entity 1}: {value}
    {entity 2}: {value}
    ...
    ```
    Ensure that your *transcripts are unformatted text with numbers spelled out*. Formatting will be taken care of by your entities, and the output from transcription engines will be unformatted.

    At the top of the `tests.txt` file, you can add "whitelists" to narrow Discovery to a particular set of intents or domains.
    In the above example, setting `intent_whitelist: digit` forces discovery to only look for entities associated with the intent `digit`.
    You can also do a `domain_whitelist`, to only allow the intents that belong to a certain domain. Comma separate values if you have multple.

    If you are using Discovery primarily as an intent classifier, you may list the "intent" as a property to be tested in the `tests.txt`:
    ```
    test: {name of test}
    transcript: {transcript you want to parse}
    intent: {expected intent}
    ```

2) The definition file, `examples/digit/custom/definitions.yaml`, contains examples that match the tests
    ```
    entities:
      room_number:
        - "@num"
    intents:
      digit:
        examples:
          - "please select @num to speak to the operator"
          - "to change your order press @num"
          - "if this is an emergency dial @num"
          - "for animal control services press @num"

    ```
    where "digit" is the name of the intent and the entities value ("room_number") match entities in `tests.txt`.

3) Edit your `discovery_config.py` to specify your "GKT_USERNAME" and "GKT_SECRETKEY" credentials.

4) Execute `python3 test_discovery.py examples/digit` to test the digit example. `test_discovery.py` launches a Discovery Docker container and performs testing on `tests.txt`, where tests pass if they have defined entities present in the most likely found intent.
    ```
    Discovery Ready
    ======
    Testing: dial number
    Test passed

    ======
    Testing: dial number
    Test passed


    (2 / 2) tests passed in 0s with 0 errors, Character error rate: 0.00%
    ```

# 2. Customization and Discovery CLI

Creating a custom project can be done by following the structure of an existing example found in the `examples` folder.

# 3. Advanced Examples and Documentation

## Testing with Real Audio

Scribe Discovery can use output from our delayed file transcription engine (SVTServer) or our real-time dictation engine (SQCServer).

For development purposes, it's easiest to first record a few audio files using your favorite software wherein you or someone else is speaking the voice commands or key phrases you want to interpret.

Then, run these files through SVTServer [following our documentation](https://transcription.greenkeytech.com/svt-e0286da/) with the SVTServer parameter `WORD_CONFUSIONS="True"` enabled when you launch the container.

For example, you can launch a single job container with the following command for a file called `test.wav`. Be sure to set `$USERNAME` and `$SECRETKEY`

```bash
docker run \
    -it \
    --rm \
    --name svtserver-test \
    -e GKT_API="https://scribeapi.greenkeytech.com/" \
    -e GKT_USERNAME="$USERNAME" \
    -e GKT_SECRETKEY="$SECRETKEY" \
    -e TARGET_FILE="/files/test.wav" \
    -v "$PWD":/files \
    -e ENABLE_CLOUD="False" \
    -e PROCS=1 \
    docker.greenkeytech.com/svtserver
```

Once complete, you should have a JSON file for each audio file you generated (e.g. `test.json` for `test.wav`). Each JSON file contains a **word confusion lattice** that Discovery searches for your target phrases.

These JSON files can be used directly with the Discovery Engine using `curl` or another http client. The example directories provide guidance on how to send these files to Discovery in the `send_transcript_to_discovery.sh` script.

For the 'digit' example, `send_transcript_to_discovery.sh` contains:
```bash
curl -X POST http://localhost:1234/discover \
     -H "Content-Type: application/json" \
     -d '{"transcript": "dial one eight"}'
```


## Full Documentation
Our full [documentation](https://transcription.greenkeytech.com/discovery-1890af/) provides many more in-depth descriptions, explanations and examples.


# Contributing

## Code of Conduct

Please make sure you read and observe our [Code of Conduct].

## Pull Request process

1. Fork it
2. Create your feature branch (`git checkout -b feature/fooBar`)
3. Commit your changes (`git commit -am 'Add some fooBar'`)
4. Push to the branch (`git push origin feature/fooBar`)
5. Create a new Pull Request

# Versioning

We use [SemVer] for versioning.  For the versions available, see the [tags on this repository].

# Authors

Original authors:

- [Ashley Shultz](https://github.com/AGiantSquid)
- [Matthew Goldey](https://github.com/mgoldey)
- [Tejas Shastry](https://github.com/tshastry)

For all others who have aided this project, please see the [list of contributors].

# License

The code in this repository is distributed under the [Apache License, Version 2.0](http://www.apache.org/licenses/LICENSE-2.0).

Copyright 2019 GreenKey Technologies

<!-- Markdown link & img defs -->
[FINOS]: https://www.finos.org
[Code of Conduct]: https://www.finos.org/code-of-conduct
[Voice Program]: https://finosfoundation.atlassian.net/wiki/spaces/VOICE/overview
[SemVer]: http://semver.org
[list of contributors]: https://github.com/finos/greenkey-discovery-sdk/graphs/contributors
[tags on this repository]: https://github.com/finos/greenkey-discovery-sdk/tags
