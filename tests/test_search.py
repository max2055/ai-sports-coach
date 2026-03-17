import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
from src.search import fetch_reference_images


def test_returns_empty_list_on_search_failure(tmp_path, mocker):
    mocker.patch("src.search.DDGS", side_effect=Exception("network error"))
    result = fetch_reference_images("tennis", tmp_path)
    assert result == []


def test_returns_empty_list_on_download_failure(tmp_path, mocker):
    mock_ddgs = MagicMock()
    mock_ddgs.__enter__ = MagicMock(return_value=mock_ddgs)
    mock_ddgs.__exit__ = MagicMock(return_value=False)
    mock_ddgs.images.return_value = [
        {"image": "http://example.com/img1.jpg"},
    ]
    mocker.patch("src.search.DDGS", return_value=mock_ddgs)
    mocker.patch("requests.get", side_effect=Exception("timeout"))

    result = fetch_reference_images("tennis", tmp_path)
    assert result == []


def test_downloads_up_to_3_images(tmp_path, mocker):
    mock_ddgs = MagicMock()
    mock_ddgs.__enter__ = MagicMock(return_value=mock_ddgs)
    mock_ddgs.__exit__ = MagicMock(return_value=False)
    mock_ddgs.images.return_value = [
        {"image": f"http://example.com/img{i}.jpg"} for i in range(5)
    ]
    mocker.patch("src.search.DDGS", return_value=mock_ddgs)

    fake_response = MagicMock()
    fake_response.raise_for_status = MagicMock()
    fake_response.content = b'\xff\xd8\xff\xd9'  # minimal JPEG bytes
    mocker.patch("requests.get", return_value=fake_response)

    result = fetch_reference_images("tennis", tmp_path)
    assert len(result) == 3
    assert all(p.suffix == ".jpg" for p in result)
