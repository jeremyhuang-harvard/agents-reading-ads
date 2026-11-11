import json
from pathlib import Path

from collect_bing_ads import choose_representative_asset, parse_assets, safe_extension


def test_parse_assets_returns_typed_asset_records():
    raw = json.dumps(
        [
            {
                "Width": 1200,
                "Height": 628,
                "AssetType": "Image",
                "AssetUrl": "https://example.test/hero?id=1",
            }
        ]
    )

    assert parse_assets(raw) == [
        {
            "width": 1200,
            "height": 628,
            "asset_type": "Image",
            "asset_url": "https://example.test/hero?id=1",
        }
    ]


def test_choose_representative_asset_prefers_largest_landscape_image():
    assets = [
        {"width": 152, "height": 152, "asset_type": "Image", "asset_url": "logo"},
        {"width": 1200, "height": 628, "asset_type": "Image", "asset_url": "hero"},
        {"width": 2048, "height": 2048, "asset_type": "Image", "asset_url": "square"},
    ]

    assert choose_representative_asset(assets)["asset_url"] == "hero"


def test_safe_extension_uses_content_type_before_url_suffix():
    assert safe_extension("https://example.test/media", "image/png") == ".png"
    assert safe_extension("https://example.test/media.jpg", "application/octet-stream") == ".jpg"
    assert safe_extension("https://example.test/media", "application/octet-stream") == ".bin"
