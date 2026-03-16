import requests
import os


API_KEY = os.getenv('ac1ae10298ce4507902e7a0cbf6aeae0')
WEBHOOK_URL = os.getenv('https://discord.com/api/webhooks/1483156092597960927/VmGU-WdHbvz2KuvB3J2fmTlph5_vAGEXzZ6tPWZpiGgKEVBsQYMNWzgNOnKguD5b4TF9')

URL = f'https://newsapi.org/v2/top-headlines?sources=fox-news&apiKey={API_KEY}'

def post_to_discord():
    try:
        data = requests.get(URL).json()
        articles = data.get('articles', [])

        if not articles:
            return

    
        news = articles[0]
        
        payload = {
            "username": "LemmeNews",
            "embeds": [{
                "title": news['title'],
                "description": news['description'] or "Click the link to read more.",
                "url": news['url'],
                "color": 15548997,
                "image": {"url": news.get('urlToImage')},
                "footer": {"text": f"Source: {news['source']['name']} | {news['publishedAt']}"}
            }]
        }

        requests.post(WEBHOOK_URL, json=payload)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    post_to_discord()
