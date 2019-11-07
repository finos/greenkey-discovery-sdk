#!/usr/bin/env python3

import streamlit as st
import requests
import json
from collections import namedtuple
from PIL import Image
import pandas as pd
import time

from testing.discovery_interface import (
  check_discovery_status,
  get_discovery_config,
  reload_discovery_config,
  submit_transcript,
)

ENCODING = "utf-8"

# TODO: add component_list
Entity = namedtuple("Entity", ["entity", "value", "tokens", "indices"])

def get_entities_from_discovery(payload):
    entities = []
    for intent in payload['intents']:
        entities += intent['entities']
    return entities


def format_component_list(component_list):
    """
  Takes a component list, like 
  [
    [
      "entity label"
      "entity value",
      some other values
    ],
  ]
  and formats it into a dictionary
  """
    formatted_values = {}
    for component in component_list:
        formatted_values[component[0]] = component[1]
    return formatted_values


def tidy_lattice_path(lattice_path):
    """
  Returns just first index of lattice path
  """
    return [_[0] for _ in lattice_path]


def format_entity_match(label, match):
    # TODO: add component_list
    # format_component_list(match['component_list'] if 'component_list' in match else []),
    return Entity(
        label,
        match['value'],
        match['interpreted_transcript'],
        tidy_lattice_path(match['lattice_path']),
    )


def format_entities(entities, config):
    # TODO: add sidebar glossary

    entity_list = []
    for entity in entities:
        label = entity["label"]
        if label not in config['entities']:
            continue
        
        for matches in entity['matches']:
            # Remove if removing GROUP_ENTITIES=True
            entity_list += [
              format_entity_match(label, match) for match in \
              (matches if isinstance(matches, (list, tuple)) else [matches]) \
            ]

    entity_list = sorted(entity_list, key=lambda e: e.indices[0] - len(e.indices) / 100)
    return pd.DataFrame.from_records(entity_list, columns=Entity._fields)


def main():
    with st.spinner("Waiting for discovery"):
        while not check_discovery_status():
            time.sleep(0.25)

    # UI FOR DEV TOOL
    logo = st.image(Image.open('logo.jpg'), width=150)
    title = st.markdown("## Discovery Interactive SDK")

    option = st.sidebar.selectbox("Mode", ["Test an interpreter", "Entity library"])

    if option == "Test an interpreter":
        # Domain / Intent Config
        config = get_discovery_config()

        domain = st.selectbox( \
          "Domain", \
          ['any'] + sorted(domain for domain in list(config['domains'].keys()) if domain != 'any') \
        )
    
        intent = st.selectbox( \
          "Intent", \
          ['any'] + sorted(intent for intent in config['domains'][domain] if intent != 'any') \
        )
    
        transcript = st.text_input("Input transcript", "eur$ 5y 3x6 5mio")

        payload = submit_transcript( \
            transcript, domain_whitelist=[domain], intent_whitelist=[intent] \
        )
    
        # Sidebar
        show_everything = st.sidebar.checkbox("Verbose discovery output", False)

        if show_everything:
            st.write(payload)

        if 'intents' in payload \
            and payload['intents'] \
            and 'entities' in payload['intents'][0]:

            show_ents = st.sidebar.checkbox("Show matched entities", True)
            if show_ents:
                entities = get_entities_from_discovery(payload)
                entity_df = format_entities(entities, config)
                st.write(entity_df)

        schema_key = st.sidebar.text_input("Schema key:", 'interpreted_quote')
        
        if schema_key and schema_key in payload.keys():
            st.write(payload[schema_key])
        
    elif option == "Entity library":
        st.write("Available entities")
        st.write({k: v if not k.startswith("_") else "[built_in]" for k,v in config['entities'].items()})

    reload_button = st.sidebar.button('Reload Discovery Config')
    if reload_button:
        with st.spinner("Reloading config"):
            if reload_discovery_config() == 'success':
                st.success('Successfully reloaded config')
            else:
                st.error('Failed to reload config')


if __name__ == "__main__":
    main()
