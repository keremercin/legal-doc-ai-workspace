from app.services.presentation import escape_html


def test_document_text_is_escaped_before_html_rendering():
    assert escape_html('<img src=x onerror="alert(1)">') == "&lt;img src=x onerror=&quot;alert(1)&quot;&gt;"
