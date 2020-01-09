# GreenKey Scribe Discovery SDK [![Build Status](https://travis-ci.org/finos/greenkey-discovery-sdk.svg?branch=master)](https://travis-ci.org/finos/greenkey-discovery-sdk)[![FINOS - Active](https://cdn.jsdelivr.net/gh/finos/contrib-toolbox@master/images/badge-active.svg)](https://finosfoundation.atlassian.net/wiki/display/FINOS/Active)
> Powerful NLP API for human conversations

<img src="https://greenkeytech.com/wp-content/uploads/2019/02/gk_logo_colorlight.png" width="300" />

---

The Discovery SDK allows you to write logic-based interpreters, and let GreenKey's Discovery engine use machine learning to identify intents and extract entities.

You can use your Discovery interpreter to power several voice- and chat-driven workflows

- Building a skill in combination with [Scribe's Real-Time Dictation](https://docs.greenkeytech.com/audio/#audioserver)

- Searching transcribed files for key phrases with [Scribe's File Transcription](https://docs.greenkeytech.com/audio/#fileserver)

- Powering chat-bot workflows using [Discovery as a service](https://docs.greenkeytech.com/nlp/#discovery)

Read more about Discovery on our [blog](https://greenkeytech.com/greenkey-scribe-discovery-skills/) or [checkout the full documentation](https://github.com/finos/greenkey-discovery-sdk/wiki)

The GreenKey Discovery SDK
is hosted by the [Voice Program] of the Fintech Open Source Foundation ([FINOS]).
If you are a company interested in the evolution of
open standards, interoperability, and innovation in the financial services sector,
please consider joining FINOS.

# Overview
1. [Quickstart](#1-quickstart)
    - Step through the 'digit' interpreter example.

2. [Customization](#2-customization)
    - Customize your own interpreter.

3. [Advanced Examples and Documentation](#3-advanced-examples-and-documentation)
    - Transcribing voice audio files with Scribe and using the Discovery engine.


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

2) The definition file, `examples/digit/custom/definitions.yaml`, contains examples that match the tests

```
entities:
  room_number:
    - "@num"
intents:
  digit:
    examples:
      - "please select @num to speak to the operator"
      - "to change your order press @room_number"
      - "if this is an emergency dial @room_number"
      - "for animal control services press @room_number"
```

where "digit" is the name of the intent and the entities value ("room_number") match entities in `tests.txt`.


# 2. Customization

Creating a custom project can be done by following the structure of an existing example found in the `examples` folder. Refer to the [wiki](https://github.com/finos/greenkey-discovery-sdk/wiki) for further information on customization


# 3. Deploying

Check out our deployment [documentation](https://docs.greenkeytech.com/nlp/#discovery) for full details on deploying Discovery.


# Contributing

## Code of Conduct

Please make sure you read and observe our [Code of Conduct].

## Pull Request process

1. Fork it
2. Create your feature branch (`git checkout -b feature/fooBar`)
3. Commit your changes (`git commit -am 'Add some fooBar'`)
4. Push to the branch (`git push origin feature/fooBar`)
5. Create a new Pull Request

_NOTE:_ Commits and pull requests to FINOS repositories will only be accepted from those contributors with an active, executed Individual Contributor License Agreement (ICLA) with FINOS OR who are covered under an existing and active Corporate Contribution License Agreement (CCLA) executed with FINOS. Commits from individuals not covered under an ICLA or CCLA will be flagged and blocked by the FINOS Clabot tool. Please note that some CCLAs require individuals/employees to be explicitly named on the CCLA.

*Need an ICLA? Unsure if you are covered under an existing CCLA? Email [help@finos.org](mailto:help@finos.org)*

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

Copyright 2020 GreenKey Technologies

<!-- Markdown link & img defs -->
[FINOS]: https://www.finos.org
[Code of Conduct]: https://www.finos.org/code-of-conduct
[Voice Program]: https://finosfoundation.atlassian.net/wiki/spaces/VOICE/overview
[SemVer]: http://semver.org
[list of contributors]: https://github.com/finos/greenkey-discovery-sdk/graphs/contributors
[tags on this repository]: https://github.com/finos/greenkey-discovery-sdk/tags
