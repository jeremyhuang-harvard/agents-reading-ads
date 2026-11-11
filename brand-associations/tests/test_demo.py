"""Offline tests for demo parsers and coders (no network)."""

from implicit_ads.demo import archive, coverage
from implicit_ads.demo.config import load_cases


def case(case_id: str) -> dict:
    return next(c for c in load_cases() if c["case_id"] == case_id)


def test_config_loads_and_validates():
    cases = load_cases()
    assert {c["case_id"] for c in cases} >= {"taylor_nb550", "kanye_energy_boost", "meghan_outland"}


def test_commerce_tags_affiliate_and_email():
    aff = archive.commerce_tags(
        "https://www.newbalance.com/pd/550/BB550V1-36007.html?irclickid=&irgwc=1&utm_source=Impact"
        "&utm_medium=Affiliate&utm_campaign=Skimbit%20Ltd.&Ecid=af_Skimbit%20Ltd."
    )
    assert aff == {"channel": "affiliate", "partner": "Skimbit Ltd."}
    ecid_only = archive.commerce_tags("https://www.newbalance.com/pd/550/BB550V1-36007.html?Ecid=af_New%20York%20Post%20Network")
    assert ecid_only == {"channel": "affiliate", "partner": "New York Post Network"}
    email = archive.commerce_tags("https://x.com/p?sc_src=email_1&utm_medium=emarsys&utm_campaign=ICYMI")
    assert email["channel"] == "email"
    assert archive.commerce_tags("https://www.newbalance.com/pd/550/BB550V1-36007.html")["channel"] == ""


def test_product_keys():
    assert archive.product_key(
        "https://www.newbalance.com/pd/550/BB550V1-42006.html?dwvar_BB550V1-42006_style=BB550VNA", "newbalance", "BB550[A-Z0-9]{3,4}"
    ) == "BB550VNA"
    assert archive.product_key("https://www.newbalance.com/pd/550/BB550V1-36007.html", "newbalance", "BB550[A-Z0-9]{3,4}") is None
    assert archive.product_key("http://www.adidas.com:80/us/energy-boost-esm-shoes/B44283.html?x=1", "adidas", r"[A-Z]\d{5}") == "B44283"
    assert archive.product_key("https://outlanddenim.com/products/harriet-in-black", "shopify", "[a-z0-9-]+") == "harriet-in-black"


def test_parsers():
    nb = (
        '"availability":"http://schema.org/InStock","price":"109.99" /is/image/NB/bb550se1_nb_02_i '
        '<a data-attr-value="7" class="x unselectable"> <a data-attr-value="8" class="x selectable">'
    )
    parsed = archive.parse_newbalance(nb)
    assert parsed["page_status"] == "InStock" and parsed["page_style"] == "BB550SE1"
    assert (parsed["sizes_available"], parsed["sizes_total"]) == (1, 2)
    shop = '{"id":1,"title":"22 / 28","option1":"22","available":false} {"id":2,"title":"23 / 28","option1":"23","available":true}'
    assert archive.parse_shopify(shop)["sizes_available"] == 1
    adi = archive.parse_adidas('<span>COMING SOON!</span> <div class="callout-bar-short">Available in 15 days</div>'
                               '<meta itemprop="availability" content="http://schema.org/OutOfStock">')
    assert adi["page_status"] == "coming_soon" and adi["countdown_days"] == 15
    template_only = archive.parse_adidas('app.resources["PREVIEW"]=" COMING SOON! Available in {0} days "; '
                                         '<meta itemprop="availability" content="http://schema.org/OutOfStock">'
                                         '<button class="button-primary addtocartbutton disabled bp-disabled" disabled><span class="text">Add To Bag</span>')
    assert template_only["page_status"] == "out_of_stock" and template_only["add_to_bag_disabled"]
    assert archive.parse_adidas('<meta itemprop="availability" content="http://schema.org/InStock">')["page_status"] == "in_stock"


def test_identification_levels():
    pats = case("taylor_nb550")["identification"]
    assert coverage.identification("Taylor Swift wore New Balance 550 BB550SE1", pats)["id_level"] == "exact"
    assert coverage.identification("Taylor Swift wore the New Balance 550 in white and red", pats)["id_level"] == "exact"
    assert coverage.identification("Taylor Swift wore New Balance 550s", pats)["id_level"] == "model"
    assert coverage.identification("Taylor Swift in New Balance sneakers", pats)["id_level"] == "brand"
    assert coverage.identification("Taylor Swift at the Chiefs game", pats)["id_level"] == "celebrity_only"


def test_published_time_and_links():
    page = '<meta property="article:published_time" content="2023-09-25T14:30:00-04:00">'
    assert coverage.published_time(page, "https://x.com/a")[0].startswith("2023-09-25")
    assert coverage.published_time("", "https://sneakernews.com/2015/05/21/foo/") == ("2015-05-21", "url_path")
    links = coverage.outbound_links(
        '<a href="https://web.archive.org/web/20230925id_/https://www.amazon.com/dp/B0?tag=thr-20">'
        '<a href="https://go.skimresources.com/?url=https%3A%2F%2Fwww.newbalance.com%2Fpd">', "https://hollywoodreporter.com/x"
    )
    found = coverage.commerce_links(links, "hollywoodreporter.com")
    assert len(found["affiliate_links"]) == 2 and len(found["retail_links"]) == 2


def test_actor_type():
    assert coverage.actor_type("https://www.complex.com/sneakers/a/x") == "specialist_sneaker"
    assert coverage.actor_type("https://pagesix.com/2023/09/25/x") == "fashion_lifestyle"
    assert coverage.actor_type("https://www.si.com/fannation/sneakers/news/x") == "specialist_sneaker"


def test_linked_level_requires_proximity():
    pats = case("kanye_energy_boost")["identification"]
    near = "Kanye performed in the adidas Energy Boost ESM in all white."
    far = "Kanye talked about Nike. " + "x " * 600 + "Unrelated adidas Energy Boost review."
    assert coverage.linked_level(near, pats) == "exact"
    assert coverage.linked_level(far, pats) == "none"


def test_outland_regex_excludes_outlander():
    pats = case("meghan_outland")["identification"]
    assert coverage.linked_level("Meghan Markle fans love Outlander season 4", pats) == "none"
    assert coverage.linked_level("Meghan wore jeans by Outland Denim", pats) == "brand"


def test_abnormal_attention_uses_weekday_baseline():
    from datetime import date, timedelta

    from implicit_ads.demo.spillover import abnormal

    start = date(2023, 8, 27)
    series = []
    for d in range(-28, 8):
        day = start + timedelta(days=d + 28)
        base = 50 if day.weekday() == 6 else 10  # Sunday-heavy series
        value = base + (d % 3) + (40 if d >= 0 and day.weekday() != 6 else 0)
        series.append((d, day.isoformat(), value))
    out = abnormal(series)
    assert out["excess_0_7"] > 25 and out["z_0_7"] > 5


def test_daily_z_does_not_leak_post_event_into_pre_period():
    from datetime import date, timedelta

    from implicit_ads.demo.spillover import daily_z

    start = date(2018, 9, 19)
    series = [(d, (start + timedelta(days=d + 28)).isoformat(), 100.0 if d == 0 else 0.0) for d in range(-28, 10)]
    out = daily_z(series)
    assert out["sparse"] and out["z"][-1] == 0 and out["z"][0] > 30
