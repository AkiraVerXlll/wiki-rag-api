import wikipediaapi
from src.settings import USER_AGENT

class WikiSaver:
    def __init__(self, path: str):
        self.path = path
        self.wiki = wikipediaapi.Wikipedia(user_agent=USER_AGENT)

    def save_article(self, topic: str, document_id: str):
        article = self.wiki.page(topic)
        if not article.exists():
            raise ValueError(f"Article {topic} does not exist.")
        full_path = f"{self.path}/{document_id}.txt"
        with open(full_path, "w") as f:
            f.write(article.text)
        return full_path