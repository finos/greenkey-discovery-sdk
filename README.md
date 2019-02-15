# GreenKey Scribe Discovery SDK [![Build Status](https://travis-ci.org/finos-voice/greenkey-discovery-sdk.svg?branch=master)](https://travis-ci.org/finos-voice/greenkey-discovery-sdk)
> Speed up business workflows through creating custom 'voice skills' and text interpreters

<img src="https://github.com/finos-voice/greenkey-voice-sdk/raw/master/logo/greenkey-logo.png" width="100" />

---

The Discovery SDK allows you to write logic-based interpreters, and let Scribe's Discovery engine use probabilistic search to identify intents and entities.

You can use your Discovery interpreter to power several voice-driven workflows such as:

- Building a skill in combination with [Scribe's Real-Time Dictation](https://transcription.greenkeytech.com/sqc-06437d7/)

- Searching transcribed files for key phrases with [Scribe's File Transcription](https://transcription.greenkeytech.com/svt-e0286da/)

Read more about Discovery on our [blog](https://www.greenkeytech.com/news/2018/07/17/greenkey-scribe-discovery-skills/) or [checkout the full documentation](https://transcription.greenkeytech.com/discovery-1890af/)

The GreenKey Discovery SDK
is hosted by the [Voice Program] of the Fintech Open Source Foundation ([FINOS]).
If you are a company interested in the evolution of
open standards, interoperability, and innovation in the financial services sector,
please consider joining FINOS.

# Overview
1. [Quickstart](#1-quickstart)
    - Step through the 'room_dialing' interpreter example.

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
This will provide you with the packages needed to run the `test_discovery.py` script, as well as the Discovery CLI.

```sh
python3 -m pip install -r requirements.txt
```

## Obtaining Credentials
[Contact Us](mailto:transcription@greenkeytech.com) to obtain credentials to obtain the Discovery Docker container from our repository and launch the Discovery engine.


## Discovery Examples Directory Overview
Each discovery example contains a folder named `custom`, which in turn contains the required two items for launching Discovery: `intents.json` and the `entities` folder.
Some examples contain a `schemas.json` file to customize the return json.
They also contain example scripts to see how the particular configuration will detect entities.

```
examples
└── room_dialing
    ├── custom
    │   ├── entities
    │   │   └── digit.py
    │   └── intents.json
    ├── send_transcript_to_discovery.sh
    └── tests.txt
```


## The 'room_dialing' Interpreter Example

1) Test cases for the room dialing example are in `examples/room_dialing/tests.txt` 
    ```
    test: dial number
    transcript: please dial eight
    digit: 8

    test: dial number
    transcript: press one eight
    digit: 1
    ...
    ```

    tests.txt follows the following format:
    ```
    test: {name of test}
    transcript: {transcript you want to parse}
    {entity 1}: {value}
    {entity 2}: {value}
    ...
    ```
    Ensure that your *transcripts are unformatted text with numbers spelled out*. Formatting will be taken care of by your entities, and the output from transcription engines will be unformatted.

2) The intents file, `examples/room_dialing/custom/intents.json`, contains examples that match the tests
    ```
    {
      "intents": [
        {
          "label": "room_dialing",
          "entities": ["digit"]
        }
      ]
    }
    ```
    where "room_dialing" is the name of the intent and the entities value ("digit") match entities in `tests.txt`.

3) Edit your `discovery_config.py` to specify your "GKT_USERNAME" and "GKT_SECRETKEY" credentials.

4) Execute `python3 test_discovery.py examples/room_dialing` to test the room_dialing example.
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


# 2. Customization and Discovery CLI
Creating a custom project can be done by following the structure of an existing example found in `examples/`. The Discovery CLI tool can also be used to guide you through creating your own project and custom definition files for use with Discovery.


## Installation
The CLI tool should already be installed from previously executing 
```sh
python3 -m pip install -r requirements.txt
```

## Usage

Once the CLI tool is installed, it is invoked with the command `gk_cli`.

You can use the tool to either create a new project, or to create an individual entity.

Before invoking the tool, navigate to the directory where you wish to create your new file or files.
- If you wish to create an entire project, navigate to the directory that will hold your `custom` folder. If you have not made your `custom` folder, the CLI will guide you through the creation of one.
- If you have already created a project, and simply wish to create an entity, navigate to your `entities` folder before running the tool. If you have not made your `entities` folder in your project, the CLI will guide you through the creation of one.

If `gk_cli` is installed, you should see the following output after invoking the tool:
```sh
$ gk_cli

? What would you like to do?  (Use arrow keys)
 ❯ Create a new entity
   Create a new project
```


# 3. Advanced Examples and Documentation

## Testing with Real Audio

Scribe Discovery can work off of output from our delayed file transcription engine (SVTServer) or our real-time dictation engine (SQCServer).

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

Once complete, you should have a JSON file for each audio file you generated (e.g. `test.json` for `test.wav`). This JSON file contains the **word confusion lattice** that Discovery searches for your target phrases.

These JSON files can be used directly with the Discovery Engine as [shown here](https://transcription.greenkeytech.com/discovery-1890af/deploying/#6-run-the-scribe-discovery-engine-on-a-file). The example directories provide guidance on how to send these files to discovery in the `send_transcript_to_discovery.sh` script.

For the 'room_dialing' example, `send_transcript_to_discovery.sh` contains:
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
1. Create your feature branch (`git checkout -b feature/fooBar`)
1. Commit your changes (`git commit -am 'Add some fooBar'`)
1. Push to the branch (`git push origin feature/fooBar`)
1. Create a new Pull Request

# Versioning

We use [SemVer] for versioning.  For the versions available, see the [tags on this repository].

# Authors

Original authors:

- [Ashley Shultz](https://github.com/AGiantSquid)
- [Matthew Goldey](https://github.com/mgoldey)
- [Tejas Shastry](https://github.com/tshastry)

For all others who have aided this project, please see the [list of contributors].

# License

This project is licensed under the Apache 2.0 License - see the [LICENSE.md](LICENSE.md) file for details.

<!-- Markdown link & img defs -->
[FINOS]: https://www.finos.org
[Code of Conduct]: https://www.finos.org/code-of-conduct
[Voice Program]: https://finosfoundation.atlassian.net/wiki/spaces/VOICE/overview
[SemVer]: http://semver.org
[list of contributors]: https://github.com/finos-voice/greenkey-discovery-sdk/graphs/contributors
[tags on this repository]: https://github.com/finos-voice/greenkey-discovery-sdk/tags
