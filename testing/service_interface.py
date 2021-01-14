#!/usr/bin/env python3

import immutables

from freeze import unfreeze


def prepare_payload(payload, external_json):
    """
    Combine payload with external_json
    """
    if isinstance(external_json, immutables.Map):
        external_json = unfreeze(external_json)

    # merge with file json when given
    if external_json is not None:
        # remove the conflicting transcript key below. The external_json tests already contain "transcript"
        if external_json.get("transcript") or external_json.get("segments"):
            del payload["transcript"]
        payload = {**external_json, **payload}
    return payload
