import os
import pytest
from src.services.wiki_saver import WikiSaver
from src.settings import DATA_PATH


@pytest.fixture
def wiki_saver():
    return WikiSaver(DATA_PATH)

def test_save_existing_page(wiki_saver):
    page_title = "Hidetaka Miyazaki"
    document_id = page_title

    article = wiki_saver.wiki.page(page_title)
    assert article.exists()
    full_path = wiki_saver.save_article(page_title, document_id)
    assert os.path.exists(full_path)

    with open(full_path, "r", encoding="utf-8") as file:
        content = file.read()
        assert len(content) > 0
        assert "Miyazaki was born on September 19" in content

    os.remove(full_path)

