import io
import json
import urllib.error
from datetime import datetime, timezone
from email.message import Message
from pathlib import Path
from typing import cast

import pytest

from collect_snap_ads import (
    StorageBudget,
    choose_primary_media,
    collect_sample,
    fetch_with_retry,
    iter_preview_records,
    load_collection_config,
    parse_args,
    read_limited,
    safe_extension,
    select_new_candidates,
)


def test_iter_preview_records_rejects_failed_subrequests():
    payload = {
        "request_status": "SUCCESS",
        "ad_previews": [
            {"sub_request_status": "SUCCESS", "ad_preview": {"id": "a1"}},
            {"sub_request_status": "FAILED", "ad_preview": {"id": "a2"}},
            {"sub_request_status": "SUCCESS"},
        ]
    }

    with pytest.raises(RuntimeError, match=r"sub_request_status=FAILED.*index=1"):
        iter_preview_records(payload)


def test_iter_preview_records_keeps_successful_records_and_ignores_missing_ads():
    payload = {
        "request_status": "SUCCESS",
        "ad_previews": [
            {"sub_request_status": "SUCCESS", "ad_preview": {"id": "a1"}},
            {"sub_request_status": "SUCCESS"},
        ],
    }

    assert iter_preview_records(payload) == [{"id": "a1"}]


def test_choose_primary_media_prefers_top_snap_creative():
    ad = {
        "top_snap_media_type": "IMAGE",
        "top_snap_media_download_link": "https://cdn.test/creative",
        "app_install_preview": {"media_download_link": "https://cdn.test/icon"},
    }

    assert choose_primary_media(ad) == {
        "role": "top_snap",
        "media_type": "IMAGE",
        "url": "https://cdn.test/creative",
    }


def test_choose_primary_media_reads_story_snap_before_app_icon():
    ad = {
        "ad_type": "STORY",
        "composite_preview": {
            "ad_snaps": [
                {"top_snap_media_type": "VIDEO"},
                {
                    "top_snap_media_type": "IMAGE",
                    "top_snap_media_download_link": "https://cdn.test/story-1",
                    "app_install_preview": {"media_download_link": "https://cdn.test/icon"},
                },
                {"top_snap_media_type": "VIDEO", "top_snap_media_download_link": "https://cdn.test/story-2"},
            ]
        },
    }

    assert choose_primary_media(ad) == {
        "role": "story_snap",
        "media_type": "IMAGE",
        "url": "https://cdn.test/story-1",
        "snap_index": 1,
        "story_snap_link_count": 2,
    }


def test_choose_primary_media_falls_back_to_app_install_media():
    ad = {
        "app_install_preview": {"media_download_link": "https://cdn.test/icon"},
    }

    assert choose_primary_media(ad) == {
        "role": "app_install_preview",
        "media_type": None,
        "url": "https://cdn.test/icon",
    }


def test_storage_budget_rejects_file_that_would_exceed_cap():
    budget = StorageBudget(max_bytes=100)
    budget.reserve(60)

    with pytest.raises(RuntimeError, match="storage budget"):
        budget.reserve(41)

    assert budget.used_bytes == 60


def test_safe_extension_uses_content_type_then_url_suffix():
    assert safe_extension("https://cdn.test/no-suffix", "image/jpeg") == ".jpg"
    assert safe_extension("https://cdn.test/video.mp4", "application/octet-stream") == ".mp4"
    assert safe_extension("https://cdn.test/blob", "application/octet-stream") == ".bin"


def test_select_new_candidates_deduplicates_and_respects_quota():
    records = [{"id": "a1"}, {"id": "a2"}, {"id": "a1"}, {"id": "a3"}]

    selected = select_new_candidates(records, seen_ids={"a2"}, quota=2)

    assert selected == [{"id": "a1"}, {"id": "a3"}]


def test_read_limited_reserves_actual_bytes():
    budget = StorageBudget(max_bytes=10)

    content = read_limited(io.BytesIO(b"abcdef"), budget=budget, per_file_max=8)

    assert content == b"abcdef"
    assert budget.used_bytes == 6


def test_read_limited_rejects_oversized_file_without_reserving_budget():
    budget = StorageBudget(max_bytes=100)

    with pytest.raises(RuntimeError, match="per-file"):
        read_limited(io.BytesIO(b"abcdef"), budget=budget, per_file_max=5)

    assert budget.used_bytes == 0


def test_collect_sample_writes_records_and_deduplicates_media(tmp_path):
    ads = [
        {
            "id": "a1",
            "paying_advertiser_name": "Example",
            "top_snap_media_type": "IMAGE",
            "top_snap_media_download_link": "https://cdn.test/a1",
        },
        {
            "id": "a2",
            "paying_advertiser_name": "Example",
            "top_snap_media_type": "IMAGE",
            "top_snap_media_download_link": "https://cdn.test/a2",
        },
    ]

    def json_fetcher(url, body):
        if body is not None:
            payload = {
                "request_status": "SUCCESS",
                "ad_previews": [
                    {"sub_request_status": "SUCCESS", "ad_preview": ad} for ad in ads
                ],
            }
        else:
            ad_id = url.rsplit("/", 1)[-1]
            payload = {"request_status": "SUCCESS", "ad_preview": next(ad for ad in ads if ad["id"] == ad_id)}
        return json.dumps(payload).encode(), 200, "application/json"

    def media_fetcher(url, per_file_max):
        assert per_file_max >= 4
        return b"same", 200, "image/jpeg"

    result = collect_sample(
        roster=[{"category": "control", "advertiser": "Example", "country": "fr", "quota": 2}],
        output_root=tmp_path,
        target=2,
        max_bytes=10_000,
        per_file_max=100,
        delay_seconds=0,
        json_fetcher=json_fetcher,
        media_fetcher=media_fetcher,
        now_fn=lambda: "2026-10-14T12:00:00+00:00",
        sleep_fn=lambda _: None,
    )

    assert result["ad_count"] == 2
    assert result["unique_media_count"] == 1
    records = [json.loads(line) for line in Path(result["records_path"]).read_text().splitlines()]
    assert [record["ad_id"] for record in records] == ["a1", "a2"]
    assert records[0]["media"]["sha256"] == records[1]["media"]["sha256"]
    assert Path(result["manifest_path"]).exists()


def test_collect_sample_reuses_search_body_for_cursor_pages(tmp_path):
    search_body = {"countries": ["fr"], "paying_advertiser_name": "Example"}
    calls = []

    def json_fetcher(url, body):
        calls.append((url, body))
        if url.endswith("/search"):
            payload = {
                "request_status": "SUCCESS",
                "paging": {"next_link": "https://api.test/search?cursor=next"},
                "ad_previews": [
                    {"sub_request_status": "SUCCESS", "ad_preview": {"id": "a1"}}
                ],
            }
        elif "cursor=next" in url:
            assert body == search_body
            payload = {
                "request_status": "SUCCESS",
                "ad_previews": [
                    {"sub_request_status": "SUCCESS", "ad_preview": {"id": "a2"}}
                ],
            }
        else:
            payload = {"request_status": "SUCCESS", "ad_preview": {"id": url.rsplit("/", 1)[-1]}}
        return json.dumps(payload).encode(), 200, "application/json"

    result = collect_sample(
        roster=[{"category": "control", "advertiser": "Example", "country": "fr", "quota": 2}],
        output_root=tmp_path,
        target=2,
        max_bytes=10_000,
        per_file_max=100,
        delay_seconds=0,
        json_fetcher=json_fetcher,
        media_fetcher=lambda url, limit: (b"", 200, "application/octet-stream"),
        now_fn=lambda: "2026-10-14T13:00:00+00:00",
        sleep_fn=lambda _: None,
    )

    assert result["ad_count"] == 2
    assert calls[0] == ("https://adsapi.snapchat.com/v1/ads_library/ads/search", search_body)


def test_collect_sample_can_skip_detail_requests_for_bulk_collection(tmp_path):
    calls = []

    def json_fetcher(url, body):
        calls.append((url, body))
        if body is None:
            raise AssertionError("detail endpoint should not be called")
        payload = {
            "request_status": "SUCCESS",
            "ad_previews": [
                {"sub_request_status": "SUCCESS", "ad_preview": {"id": "a1"}}
            ],
        }
        return json.dumps(payload).encode(), 200, "application/json"

    result = collect_sample(
        roster=[{"category": "control", "advertiser": "Example", "country": "fr", "quota": 1}],
        output_root=tmp_path,
        target=1,
        max_bytes=10_000,
        per_file_max=100,
        delay_seconds=0,
        detail_limit=0,
        json_fetcher=json_fetcher,
        media_fetcher=lambda url, limit: (b"", 200, "application/octet-stream"),
        now_fn=lambda: "2026-10-14T14:00:00+00:00",
        sleep_fn=lambda _: None,
    )

    assert result["ad_count"] == 1
    assert result["detail_request_count"] == 0
    assert len(calls) == 1


def test_collect_sample_retries_transient_search_response(tmp_path):
    attempts = 0
    sleeps = []

    def json_fetcher(url, body):
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            return b"temporarily unavailable", 503, "text/plain"
        payload = {
            "request_status": "SUCCESS",
            "ad_previews": [
                {"sub_request_status": "SUCCESS", "ad_preview": {"id": "a1"}}
            ],
        }
        return json.dumps(payload).encode(), 200, "application/json"

    result = collect_sample(
        roster=[{"category": "control", "advertiser": "Example", "country": "fr", "quota": 1}],
        output_root=tmp_path,
        target=1,
        max_bytes=10_000,
        per_file_max=100,
        delay_seconds=0,
        json_fetcher=json_fetcher,
        media_fetcher=lambda url, limit: (b"", 200, "application/octet-stream"),
        now_fn=lambda: "2026-10-14T14:30:00+00:00",
        sleep_fn=sleeps.append,
        retry_attempts=2,
        retry_base_seconds=1,
        retry_max_seconds=10,
    )

    assert result["ad_count"] == 1
    assert attempts == 2
    assert sleeps == [1]


def test_collect_sample_retries_http_error_without_headers(tmp_path):
    attempts = 0
    sleeps = []

    def json_fetcher(url, body):
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            raise urllib.error.HTTPError(
                url, 502, "bad gateway", cast(Message, None), None
            )
        payload = {
            "request_status": "SUCCESS",
            "ad_previews": [
                {"sub_request_status": "SUCCESS", "ad_preview": {"id": "a1"}}
            ],
        }
        return json.dumps(payload).encode(), 200, "application/json"

    result = collect_sample(
        roster=[{"category": "control", "advertiser": "Example", "country": "fr", "quota": 1}],
        output_root=tmp_path,
        target=1,
        max_bytes=10_000,
        per_file_max=100,
        delay_seconds=0,
        json_fetcher=json_fetcher,
        media_fetcher=lambda url, limit: (b"", 200, "application/octet-stream"),
        now_fn=lambda: "2026-10-14T14:30:30+00:00",
        sleep_fn=sleeps.append,
        retry_attempts=2,
        retry_base_seconds=2,
        retry_max_seconds=10,
    )

    assert result["ad_count"] == 1
    assert attempts == 2
    assert sleeps == [2]


def test_collect_sample_retries_transient_detail_response(tmp_path):
    detail_attempts = 0
    sleeps = []

    def json_fetcher(url, body):
        nonlocal detail_attempts
        if body is not None:
            payload = {
                "request_status": "SUCCESS",
                "ad_previews": [
                    {"sub_request_status": "SUCCESS", "ad_preview": {"id": "a1"}}
                ],
            }
            return json.dumps(payload).encode(), 200, "application/json"
        detail_attempts += 1
        if detail_attempts == 1:
            return b"busy", 500, "text/plain"
        payload = {"request_status": "SUCCESS", "ad_preview": {"id": "a1", "headline": "detail"}}
        return json.dumps(payload).encode(), 200, "application/json"

    result = collect_sample(
        roster=[{"category": "control", "advertiser": "Example", "country": "fr", "quota": 1}],
        output_root=tmp_path,
        target=1,
        max_bytes=10_000,
        per_file_max=100,
        delay_seconds=0,
        detail_limit=1,
        json_fetcher=json_fetcher,
        media_fetcher=lambda url, limit: (b"", 200, "application/octet-stream"),
        now_fn=lambda: "2026-10-14T14:31:00+00:00",
        sleep_fn=sleeps.append,
        retry_attempts=2,
        retry_base_seconds=1,
        retry_max_seconds=10,
    )

    record = json.loads(Path(result["records_path"]).read_text())
    assert detail_attempts == 2
    assert record["detail_error"] is None
    assert record["ad"]["headline"] == "detail"
    assert sleeps == [1]


def test_collect_sample_retries_media_using_numeric_retry_after(tmp_path):
    media_attempts = 0
    sleeps = []

    def json_fetcher(url, body):
        payload = {
            "request_status": "SUCCESS",
            "ad_previews": [
                {
                    "sub_request_status": "SUCCESS",
                    "ad_preview": {
                        "id": "a1",
                        "top_snap_media_download_link": "https://cdn.test/a1",
                    },
                }
            ],
        }
        return json.dumps(payload).encode(), 200, "application/json"

    def media_fetcher(url, limit):
        nonlocal media_attempts
        media_attempts += 1
        if media_attempts == 1:
            headers = Message()
            headers["Retry-After"] = "7.5"
            raise urllib.error.HTTPError(
                url, 429, "rate limited", headers, None
            )
        return b"creative", 200, "image/jpeg"

    result = collect_sample(
        roster=[{"category": "control", "advertiser": "Example", "country": "fr", "quota": 1}],
        output_root=tmp_path,
        target=1,
        max_bytes=10_000,
        per_file_max=100,
        delay_seconds=0,
        json_fetcher=json_fetcher,
        media_fetcher=media_fetcher,
        now_fn=lambda: "2026-10-14T14:32:00+00:00",
        sleep_fn=sleeps.append,
        retry_attempts=2,
        retry_base_seconds=1,
        retry_max_seconds=2,
    )

    record = json.loads(Path(result["records_path"]).read_text())
    assert media_attempts == 2
    assert record["media_error"] is None
    assert record["media"]["byte_length"] == 8
    assert sleeps == [2]


@pytest.mark.parametrize(
    ("retry_after", "expected_delay"),
    [
        ("9999", 3),
        ("-4", 0),
        ("not-a-delay", 2),
    ],
)
def test_fetch_with_retry_clamps_or_rejects_numeric_retry_after(
    retry_after, expected_delay
):
    attempts = 0
    sleeps = []

    def fetcher():
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            headers = Message()
            headers["Retry-After"] = retry_after
            raise urllib.error.HTTPError("https://api.test", 429, "busy", headers, None)
        return b"ok", 200, "text/plain"

    assert fetch_with_retry(
        fetcher,
        retry_attempts=2,
        retry_base_seconds=2,
        retry_max_seconds=3,
        sleep_fn=sleeps.append,
        clock_fn=lambda: datetime(2026, 10, 20, 12, 0, tzinfo=timezone.utc),
    ) == (b"ok", 200, "text/plain")
    assert sleeps == [expected_delay]


def test_fetch_with_retry_supports_http_date_retry_after_with_injected_clock():
    attempts = 0
    sleeps = []

    def fetcher():
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            headers = Message()
            headers["Retry-After"] = "Tue, 20 Oct 2026 12:00:08 GMT"
            raise urllib.error.HTTPError("https://api.test", 429, "busy", headers, None)
        return b"ok", 200, "text/plain"

    fetch_with_retry(
        fetcher,
        retry_attempts=2,
        retry_base_seconds=1,
        retry_max_seconds=5,
        sleep_fn=sleeps.append,
        clock_fn=lambda: datetime(2026, 10, 20, 12, 0, tzinfo=timezone.utc),
    )

    assert sleeps == [5]


def test_collect_sample_does_not_retry_ordinary_client_error(tmp_path):
    attempts = 0
    sleeps = []

    def json_fetcher(url, body):
        nonlocal attempts
        attempts += 1
        return b"not found", 404, "text/plain"

    with pytest.raises(RuntimeError, match="HTTP status 404"):
        collect_sample(
            roster=[{"category": "control", "advertiser": "Example", "country": "fr", "quota": 1}],
            output_root=tmp_path,
            target=1,
            max_bytes=10_000,
            per_file_max=100,
            delay_seconds=0,
            json_fetcher=json_fetcher,
            now_fn=lambda: "2026-10-14T14:33:00+00:00",
            sleep_fn=sleeps.append,
            retry_attempts=4,
        )

    assert attempts == 1
    assert sleeps == []


def test_collect_sample_raises_after_transient_retries_are_exhausted(tmp_path):
    attempts = 0
    sleeps = []

    def json_fetcher(url, body):
        nonlocal attempts
        attempts += 1
        return b"busy", 503, "text/plain"

    with pytest.raises(RuntimeError, match="HTTP status 503"):
        collect_sample(
            roster=[{"category": "control", "advertiser": "Example", "country": "fr", "quota": 1}],
            output_root=tmp_path,
            target=1,
            max_bytes=10_000,
            per_file_max=100,
            delay_seconds=0,
            json_fetcher=json_fetcher,
            now_fn=lambda: "2026-10-14T14:34:00+00:00",
            sleep_fn=sleeps.append,
            retry_attempts=4,
            retry_base_seconds=2,
            retry_max_seconds=3,
        )

    assert attempts == 4
    assert sleeps == [2, 3, 3]


def test_parse_args_exposes_retry_configuration(monkeypatch):
    monkeypatch.setattr(
        "sys.argv",
        [
            "collect_snap_ads.py",
            "--retry-attempts",
            "6",
            "--retry-base-seconds",
            "2.5",
            "--retry-max-seconds",
            "45",
        ],
    )

    args = parse_args()

    assert args.retry_attempts == 6
    assert args.retry_base_seconds == 2.5
    assert args.retry_max_seconds == 45


def test_load_collection_config_honors_object_roster_defaults(tmp_path):
    path = tmp_path / "roster.json"
    path.write_text(
        json.dumps(
            {
                "target": 5000,
                "storage_cap_gib": 30,
                "per_file_max_mib": 256,
                "strata": [
                    {
                        "category": "sports_betting",
                        "advertiser": "Example",
                        "country": "fr",
                        "quota": 1000,
                    }
                ],
            }
        )
    )

    config = load_collection_config(path)

    assert config.target == 5000
    assert config.max_storage_gb == 30
    assert config.per_file_max_mb == 256


def test_load_collection_config_preserves_list_roster_defaults(tmp_path):
    path = tmp_path / "roster.json"
    path.write_text(
        json.dumps(
            [
                {
                    "category": "control",
                    "advertiser": "Example",
                    "country": "fr",
                    "quota": 100,
                }
            ]
        )
    )

    config = load_collection_config(path)

    assert config.target == 100
    assert config.max_storage_gb == 30
    assert config.per_file_max_mb == 512


def test_load_collection_config_cli_values_override_roster_settings(tmp_path):
    path = tmp_path / "roster.json"
    path.write_text(
        json.dumps(
            {
                "target": 5000,
                "storage_cap_gib": 30,
                "per_file_max_mib": 256,
                "strata": [
                    {
                        "category": "sports_betting",
                        "advertiser": "Example",
                        "country": "fr",
                        "quota": 1000,
                    }
                ],
            }
        )
    )

    config = load_collection_config(
        path,
        target_override=7,
        max_storage_gb_override=8,
        per_file_max_mb_override=9,
    )

    assert config.target == 7
    assert config.max_storage_gb == 8
    assert config.per_file_max_mb == 9


def test_five_firm_config_resolves_to_5000_records_and_declared_storage():
    config = load_collection_config(
        Path("config/snap_fr_sports_betting_competitors_5x1000_v1.json")
    )

    assert config.target == 5000
    assert config.max_storage_gb == 30
    assert config.per_file_max_mb == 512


def test_collect_sample_rejects_http_200_search_request_error(tmp_path):
    def json_fetcher(url, body):
        payload = {
            "request_status": "ERROR",
            "request_id": "request-123",
            "error_code": "INVALID_REQUEST",
            "ad_previews": [],
        }
        return json.dumps(payload).encode(), 200, "application/json"

    with pytest.raises(
        RuntimeError,
        match=r"request_status=ERROR.*request_id=request-123.*error_code=INVALID_REQUEST",
    ):
        collect_sample(
            roster=[{"category": "control", "advertiser": "Example", "country": "fr", "quota": 1}],
            output_root=tmp_path,
            target=1,
            max_bytes=10_000,
            per_file_max=100,
            delay_seconds=0,
            json_fetcher=json_fetcher,
            now_fn=lambda: "2026-10-20T14:00:00+00:00",
            sleep_fn=lambda _: None,
        )

    assert list(tmp_path.glob("**/manifest.json")) == []


def test_collect_sample_rejects_failed_search_subrequest(tmp_path):
    def json_fetcher(url, body):
        payload = {
            "request_status": "SUCCESS",
            "ad_previews": [
                {
                    "sub_request_status": "ERROR",
                    "sub_request_id": "subrequest-9",
                    "error_code": "INTERNAL_ERROR",
                }
            ],
        }
        return json.dumps(payload).encode(), 200, "application/json"

    with pytest.raises(
        RuntimeError,
        match=r"sub_request_status=ERROR.*sub_request_id=subrequest-9.*error_code=INTERNAL_ERROR",
    ):
        collect_sample(
            roster=[{"category": "control", "advertiser": "Example", "country": "fr", "quota": 1}],
            output_root=tmp_path,
            target=1,
            max_bytes=10_000,
            per_file_max=100,
            delay_seconds=0,
            json_fetcher=json_fetcher,
            now_fn=lambda: "2026-10-20T14:01:00+00:00",
            sleep_fn=lambda _: None,
        )

    assert list(tmp_path.glob("**/manifest.json")) == []


def test_collect_sample_marks_search_exhausted_when_pagination_ends_naturally(tmp_path):
    def json_fetcher(url, body):
        payload = {"request_status": "SUCCESS", "ad_previews": []}
        return json.dumps(payload).encode(), 200, "application/json"

    result = collect_sample(
        roster=[{"category": "control", "advertiser": "Example", "country": "fr", "quota": 2}],
        output_root=tmp_path,
        target=2,
        max_bytes=10_000,
        per_file_max=100,
        delay_seconds=0,
        json_fetcher=json_fetcher,
        media_fetcher=lambda url, limit: (b"", 200, "application/octet-stream"),
        now_fn=lambda: "2026-10-14T15:00:00+00:00",
        sleep_fn=lambda _: None,
    )

    assert result["strata"][0]["search_exhausted"] is True
    assert result["strata"][0]["truncation_reason"] is None


def test_collect_sample_records_quota_truncation(tmp_path):
    def json_fetcher(url, body):
        payload = {
            "request_status": "SUCCESS",
            "paging": {"next_link": "https://api.test/search?cursor=next"},
            "ad_previews": [
                {"sub_request_status": "SUCCESS", "ad_preview": {"id": "a1"}}
            ],
        }
        return json.dumps(payload).encode(), 200, "application/json"

    result = collect_sample(
        roster=[{"category": "control", "advertiser": "Example", "country": "fr", "quota": 1}],
        output_root=tmp_path,
        target=2,
        max_bytes=10_000,
        per_file_max=100,
        delay_seconds=0,
        json_fetcher=json_fetcher,
        media_fetcher=lambda url, limit: (b"", 200, "application/octet-stream"),
        now_fn=lambda: "2026-10-14T16:00:00+00:00",
        sleep_fn=lambda _: None,
    )

    assert result["strata"][0]["search_exhausted"] is False
    assert result["strata"][0]["truncation_reason"] == "quota"


def test_collect_sample_records_global_target_truncation(tmp_path):
    def json_fetcher(url, body):
        payload = {
            "request_status": "SUCCESS",
            "paging": {"next_link": "https://api.test/search?cursor=next"},
            "ad_previews": [
                {"sub_request_status": "SUCCESS", "ad_preview": {"id": "a1"}}
            ],
        }
        return json.dumps(payload).encode(), 200, "application/json"

    result = collect_sample(
        roster=[{"category": "control", "advertiser": "Example", "country": "fr", "quota": 2}],
        output_root=tmp_path,
        target=1,
        max_bytes=10_000,
        per_file_max=100,
        delay_seconds=0,
        json_fetcher=json_fetcher,
        media_fetcher=lambda url, limit: (b"", 200, "application/octet-stream"),
        now_fn=lambda: "2026-10-14T17:00:00+00:00",
        sleep_fn=lambda _: None,
    )

    assert result["strata"][0]["search_exhausted"] is False
    assert result["strata"][0]["truncation_reason"] == "global_target"


def test_collect_sample_records_max_pages_truncation(tmp_path):
    def json_fetcher(url, body):
        payload = {
            "request_status": "SUCCESS",
            "paging": {"next_link": "https://api.test/search?cursor=next"},
            "ad_previews": [],
        }
        return json.dumps(payload).encode(), 200, "application/json"

    result = collect_sample(
        roster=[{"category": "control", "advertiser": "Example", "country": "fr", "quota": 1}],
        output_root=tmp_path,
        target=1,
        max_bytes=10_000,
        per_file_max=100,
        delay_seconds=0,
        json_fetcher=json_fetcher,
        media_fetcher=lambda url, limit: (b"", 200, "application/octet-stream"),
        now_fn=lambda: "2026-10-14T18:00:00+00:00",
        sleep_fn=lambda _: None,
        max_pages_per_stratum=1,
    )

    assert result["strata"][0]["search_exhausted"] is False
    assert result["strata"][0]["truncation_reason"] == "max_pages"


def test_collect_sample_records_storage_budget_truncation(tmp_path):
    def json_fetcher(url, body):
        payload = {
            "request_status": "SUCCESS",
            "ad_previews": [
                {
                    "sub_request_status": "SUCCESS",
                    "ad_preview": {
                        "id": "a1",
                        "top_snap_media_download_link": "https://cdn.test/a1",
                    },
                }
            ],
        }
        return json.dumps(payload).encode(), 200, "application/json"

    result = collect_sample(
        roster=[{"category": "control", "advertiser": "Example", "country": "fr", "quota": 1}],
        output_root=tmp_path,
        target=1,
        max_bytes=2_000,
        per_file_max=4_000,
        delay_seconds=0,
        json_fetcher=json_fetcher,
        media_fetcher=lambda url, limit: (b"x" * 3_000, 200, "application/octet-stream"),
        now_fn=lambda: "2026-10-14T19:00:00+00:00",
        sleep_fn=lambda _: None,
    )

    assert result["budget_exhausted"] is True
    assert result["strata"][0]["search_exhausted"] is False
    assert result["strata"][0]["truncation_reason"] == "storage_budget"
