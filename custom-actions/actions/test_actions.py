from actions import actions
import pytest


def test_get_request_keywords_url():

    assert (
        actions.get_request_keywords_url("barrage éolienne", "hydrauélectrique")
        == "https://trouver.datasud.fr/api/3/action/package_search?q=barrage||éolienne||hydrauélectrique"
    ), "Datasud Request URL failed"

    assert (
        actions.get_request_keywords_url("", "hydrauélectrique électrique")
        == "https://trouver.datasud.fr/api/3/action/package_search?q=hydrauélectrique||électrique"
    ), "Datasud Request URL failed"

    assert (
        actions.get_request_keywords_url("barrage éolienne", "")
        == "https://trouver.datasud.fr/api/3/action/package_search?q=barrage||éolienne"
    ), "Datasud Request URL failed"

