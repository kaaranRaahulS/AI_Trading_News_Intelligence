import requests 
import feedparser
from bs4 import BeautifulSoup
# from newspaper import Article
from urllib.parse import quote #This converts string into valid URL - Gold News -> Gold%20News - %20 for space, %26 for &, %2F for /, %3f for question

def FetchNews(query, numOfArticles=10):
    try:
        response = requests.get(f"https://news.google.com/rss/search?q={quote(query)}", timeout = 10)
        response.raise_for_status()

        feed = feedparser.parse(response.content)
        news_items = feed.entries[:numOfArticles]

        articles = []
        for article in news_items:
            title = article.title,
            published = article.published,
            link = article.link,
            content = fetch_content_from_link(article.link)

            articles.append({
                "title": title,
                "published" : article.published,
                "link" : link,
                "content": content
            })
        return articles

    except requests.exceptions.RequestException as e:
        print(f"Error fetching RSS feed: {e}")

def fetch_content_from_link(link):
    try:
        # article = Article(link)
        # article.download()
        # article.parse()
        # print (article.text)

        response = requests.get(link, timeout = 10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        paragraphs = soup.find_all('p')
        content = ' '.join([p.get_text() for p in paragraphs])
        return content.strip()

    except requests.RequestException:
        return "Content cannot be retrieved."




if __name__ == "__main__":
    print(FetchNews("Gold", 10))
