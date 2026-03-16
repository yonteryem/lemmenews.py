import requests

WEBHOOK_URL = "https://discord.com/api/webhooks/1483156092597960927/VmGU-WdHbvz2KuvB3J2fmTlph5_vAGEXzZ6tPWZpiGgKEVBsQYMNWzgNOnKguD5b4TF9"

# Fox News RSS feed converted to JSON automatically (No API Key needed)
RSS_URL = "https://moxie.foxnews.com/google-publisher/latest.xml"
API_URL = f"https://api.rss2json.com/v1/api.json?rss_url={RSS_URL}"

def post_to_discord():
    try:
        response = requests.get(API_URL).json()
        articles = response.get('items', [])

        if not articles:
            print("No news found.")
            return

        # Grab the newest article
        news = articles[0]
        
        # Pulling the image from the RSS feed data
        img_url = news.get('thumbnail', '')
        if not img_url and isinstance(news.get('enclosure'), dict):
            img_url = news['enclosure'].get('link', '')

        payload = {
            "username": "LemmeNews",
            "embeds": [{
                "title": news['title'],
                "description": news['description'][:500] + "..." if news.get('description') else "Click the link to read more.",
                "url": news['link'],
                "color": 15548997,
                "image": {"url": img_url} if img_url else {},
                "footer": {"text": f"Fox News | {news['pubDate']}"}
            }]
        }

        requests.post(WEBHOOK_URL, json=payload)
        print("News sent!")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    post_to_discord()
