import translate_page as tp


def test_numbers_are_placeholders_and_refilled_in_order():
    table = {"Q{n} {n} revenue grew {n}% to ${n}M.": "Q{n} {n} 收入增长 {n}% 至 ${n}M。"}
    html, missing = tp.translate("<p>Q3 2026 revenue grew 27% to $275.4M.</p>", table)
    assert html == "<p>Q3 2026 收入增长 27% 至 $275.4M。</p>" and not missing


def test_unknown_text_stays_english_and_entities_round_trip():
    table = {"AI drug discovery & protein design": "AI 药物研发与蛋白质设计"}
    html, missing = tp.translate("<td>AI drug discovery &amp; protein design</td><a href='x'>Some headline</a>", table)
    assert "<td>AI 药物研发与蛋白质设计</td>" in html
    assert "Some headline" in html and "link: Some headline" in missing


def test_style_blocks_and_mismatched_placeholders_are_left_alone():
    table = {"color": "颜色", "Top {n}": "前 {n} {n}"}
    html, _ = tp.translate("<style>.a{color:red}</style><p>Top 5</p>", table)
    assert "<style>.a{color:red}</style>" in html and "<p>Top 5</p>" in html
