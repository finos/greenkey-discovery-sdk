#!/usr/bin/env python3

import os
from collections import namedtuple

import dotenv
import pandas as pd
import requests
import streamlit as st
from PIL import Image
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from launch import wait_on_service
from testing.discovery_interface import (
    reload_discovery_config,
    submit_discovery_transcript,
)

env = dotenv.dotenv_values("client.env")


class RetryRequest(Retry):
    """
    Custom retry class with max backoff set to TIMEOUT from client.env
    """

    BACKOFF_MAX = float(env["TIMEOUT"])


retries = RetryRequest(
    total=int(env["RETRIES"]), backoff_factor=1.0, status_forcelist=[500, 502, 503, 504]
)
request_session = requests.Session()
request_session.mount("http://", HTTPAdapter(max_retries=retries))

ENCODING = "utf-8"

# None here prints all dataframe rows
display_rows = int(os.environ.get("DISCOVERY_DISPLAY_ROWS", 0))
pd.set_option("display.max_rows", display_rows if display_rows > 0 else None)

# TODO: add component_list
Entity = namedtuple("Entity", ["entity", "value", "tokens", "indices"])


def get_entities_from_discovery(payload):
    entities = []
    for intent in payload["intents"]:
        entities += intent["entities"]
    return entities


def format_component_list(component_list):
    # Takes a component list, like
    # [
    #   [
    #     "entity label"
    #     "entity value",
    #     some other values
    #   ],
    # ]
    # and formats it into a dictionary
    # in comment instead of docstring due to https://github.com/streamlit/streamlit/issues/533
    formatted_values = {}
    for component in component_list:
        formatted_values[component[0]] = component[1]
    return formatted_values


def tidy_lattice_path(lattice_path):
    # Returns just first index of lattice path
    # in comment instead of docstring due to https://github.com/streamlit/streamlit/issues/533
    return [_[0] for _ in lattice_path]


def format_entity_match(label, match):
    # TODO: add component_list
    # format_component_list(match["component_list"] if "component_list" in match else []),
    return Entity(
        label,
        match["value"],
        match["interpreted_transcript"],
        tidy_lattice_path(match["lattice_path"]),
    )


def get_entity_matches(label, entity):
    entity_list = []
    for matches in entity["matches"]:
        # Remove if removing GROUP_ENTITIES=True
        entity_list += [
            format_entity_match(label, match)
            for match in (matches if isinstance(matches, (list, tuple)) else [matches])
        ]
    return entity_list


def format_entities(entities, config):
    # TODO: add sidebar glossary
    entity_list = []
    for entity in entities:
        label = entity["label"]
        if label not in config["entities"]:
            continue

        entity_list += get_entity_matches(label, entity)

    entity_list = sorted(entity_list, key=lambda e: e.indices[0] - len(e.indices) / 100)
    return pd.DataFrame.from_records(entity_list, columns=Entity._fields)


def show_matched_entities(payload, config, show_ents):
    if show_ents:
        entities = get_entities_from_discovery(payload)
        entity_df = format_entities(entities, config)
        st.write(entity_df)


def reload_discovery():
    with st.spinner("Reloading config"):
        if reload_discovery_config():
            st.success("Successfully reloaded config")
        else:
            st.error("Failed to reload config")


def set_intent(config):
    intent = st.selectbox("Intent", config["intents"])
    return intent


def test_an_interpreter(config):
    intent = set_intent(config)

    transcript = st.text_area("Input transcript", "eur$ 5y 3x6 5mio")

    payload = submit_discovery_transcript(transcript, [intent])

    # Sidebar
    show_everything = st.sidebar.checkbox("Verbose discovery output", False)
    show_ents = st.sidebar.checkbox("Show matched entities", True)

    if show_everything:
        st.write(payload)

    if (
        "intents" in payload
        and payload["intents"]
        and "entities" in payload["intents"][0]
    ):

        show_matched_entities(payload, config, show_ents)

    schema_key = st.sidebar.text_input("Schema key:", "interpreted_quote")

    if schema_key and schema_key in payload.keys():
        st.write(payload[schema_key])


def entity_library(config):
    st.write("Available entities")
    st.write(
        {
            k: v
            if not k.startswith("_")
            else {"[built-in]": {"samples": v.get("samples", [])}}
            for k, v in config["entities"].items()
        }
    )


def main():
    with st.spinner("Waiting for discovery"):
        wait_on_service(":".join([env["DISCOVERY_HOST"], env["DISCOVERY_PORT"]]))

    # UI FOR DEV TOOL
    st.image(Image.open("logo.jpg"), width=150)
    st.markdown("## Discovery Interactive SDK")

    reload_button = st.sidebar.button("Reload Discovery Config")

    if reload_button:
        reload_discovery()

    option = st.sidebar.selectbox("Mode", ["Test an interpreter", "Entity library"])

    # Domain / Intent Config
    config = request_session.get(
        f"{env['DISCOVERY_HOST']}:{env['DISCOVERY_PORT']}/developer"
    ).json()

    if option == "Test an interpreter":
        test_an_interpreter(config)

    elif option == "Entity library":
        entity_library(config)


if __name__ == "__main__":
    main()
