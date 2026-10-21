from app.providers.sources import categorize, relevance


def test_news_category_uses_article_language():
    assert categorize("Central bank cuts its interest rate") == "Rates & central banks"


def test_relevance_is_capped_and_is_only_an_estimate():
    score = relevance("Earnings and inflation forecast", "Rate policy and merger activity")
    assert 0 <= score <= 5
