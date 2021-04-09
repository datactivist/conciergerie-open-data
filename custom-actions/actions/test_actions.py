from actions import actions
import pytest


def test_get_request_keywords_url():

    assert (
        actions.get_request_keywords_url("barrage éolienne", "hydroélectrique")
        == "https://trouver.datasud.fr/api/3/action/package_search?q=barrage||éolienne||hydroélectrique"
    ), "Datasud Request URL failed"

    assert (
        actions.get_request_keywords_url("", "hydroélectrique électrique")
        == "https://trouver.datasud.fr/api/3/action/package_search?q=hydroélectrique||électrique"
    ), "Datasud Request URL failed"

    assert (
        actions.get_request_keywords_url("barrage éolienne", "")
        == "https://trouver.datasud.fr/api/3/action/package_search?q=barrage||éolienne"
    ), "Datasud Request URL failed"

