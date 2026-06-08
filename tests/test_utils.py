from app.utils import extract_app_id


def test_extract_app_id_from_clean_url() -> None:
    url = "https://store.steampowered.com/app/858710/"
    assert extract_app_id(url) == "858710"


def test_extract_app_id_from_url_with_query_params() -> None:
    url = "https://store.steampowered.com/app/858710/?curator_clanid=4777282"
    assert extract_app_id(url) == "858710"


def test_extract_app_id_returns_none_for_invalid_url() -> None:
    assert extract_app_id("https://example.com/no-app-id") is None
