import people_activity as pa


def test_talks_needs_name_and_talk_words():
    arts = [{"title": "Tempus to Present at the Piper Sandler Healthcare Conference - Business Wire", "published_at": "Mon, 23 Nov 2026 12:00:00 GMT", "url": "u1"},
            {"title": "Tempus to Present at the Piper Sandler Healthcare Conference - Yahoo", "published_at": "Mon, 23 Nov 2026 13:00:00 GMT", "url": "u2"},
            {"title": "Tempus shares fall after earnings - CNBC", "published_at": "Mon, 23 Nov 2026 12:00:00 GMT", "url": "u3"},
            {"title": "Rival to present at conference - X", "published_at": "Mon, 23 Nov 2026 12:00:00 GMT", "url": "u4"}]
    out = pa.talks(arts, "Tempus")
    assert len(out) == 1 and out[0]["date"] == "2026-11-23" and "Piper Sandler Healthcare Conference" in out[0]["venue"]


def test_build_people_and_company():
    def fake(query):
        if "Jane Roe" in query:
            return [{"title": "Jane Roe keynote at ASCO Breakthrough Summit - Org", "published_at": "Tue, 10 Nov 2026 10:00:00 GMT", "url": "p"}]
        return []
    out = pa.build(["ACME"], {"ACME": {"company": "Acme Bio, Inc."}},
                   {"ACME": {"people": [{"name": "Jane Roe", "founder": True, "title": "CSO"}]}}, fetch=fake, pause=0)
    assert out["summary"]["peopleTalks"] == 1 and out["companies"]["ACME"]["peopleTalks"][0]["person"] == "Jane Roe"


def test_advisory_panel_is_not_a_talk():
    arts = [{"title": "GRAIL Surged After FDA Panel Backed Its Cancer Detection Test - Yahoo", "published_at": "Mon, 03 Nov 2026 12:00:00 GMT", "url": "x"}]
    assert pa.talks(arts, "GRAIL") == []
