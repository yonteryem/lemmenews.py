
import os
import time
import html
import requests
import hashlib
import json
from pathlib import Path

# ==============================
# KnowBetter - Fox News Bot
# ==============================

WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "").strip()

RSS_URL = "https://moxie.foxnews.com/google-publisher/latest.xml"
API_URL = "https://api.rss2json.com/v1/api.json"

CHECK_INTERVAL = 300  # Check every 5 minutes
STATE_FILE = Path("knowbetter_state.json")

SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": "KnowBetterNewsBot/1.0"
})


def load_last_article():
    """Load the previously posted article ID."""
    try:
        if STATE_FILE.exists():
            data = json.loads(STATE_FILE.read_text(encoding="utf-8"))
            return data.get("last_article", "")
    except (OSError, ValueError):
        print("Warning: Could not read saved state.")

    return ""


def save_last_article(article_id):
    """Save the article ID to prevent duplicate posts."""
    try:
        STATE_FILE.write_text(
            json.dumps({"last_article": article_id}),
            encoding="utf-8"
        )
    except OSError as error:
        print(f"Warning: Could not save state: {error}")


def get_latest_article():
    """Fetch the latest article from Fox News RSS."""
    response = SESSION.get(
        API_URL,
        params={"rss_url": RSS_URL},
        timeout=20
    )
    response.raise_for_status()

    data = response.json()

    if data.get("status") != "ok":
        raise RuntimeError(
            data.get("message", "RSS2JSON returned an error.")
        )

    articles = data.get("items", [])

    if not articles:
        return None

    return articles[0]


def get_article_id(article):
    """Generate a stable ID for an article."""
    identifier = (
        article.get("guid")
        or article.get("link")
        or article.get("title")
        or ""
    )

    return hashlib.sha256(
        identifier.encode("utf-8")
    ).hexdigest()


def get_article_image(article):
    """Find the article thumbnail or enclosure image."""
    thumbnail = article.get("thumbnail", "")

    if isinstance(thumbnail, str) and thumbnail.startswith("https://"):
        return thumbnail

    enclosure = article.get("enclosure")

    if isinstance(enclosure, dict):
        image_url = enclosure.get("link", "")

        if isinstance(image_url, str) and image_url.startswith("https://"):
            return image_url

    return ""


def post_to_discord(article):
    """Send an article embed to Discord."""
    title = html.unescape(
        article.get("title") or "Latest Fox News"
    )

    description = html.unescape(
        article.get("description") or "Click to read the full article."
    )

    link = article.get("link", "")
    pub_date = article.get("pubDate", "Unknown date")
    image_url = get_article_image(article)

    # Discord embed limits
    title = title[:256]
    description = description[:4000]

    embed = {
        "title": title,
        "description": description,
        "color": 15548997,
        "footer": {
            "text": f"Fox News | {pub_date}"[:2048]
        }
    }

    if link.startswith(("https://", "http://")):
        embed["url"] = link

    if image_url:
        embed["image"] = {"url": image_url}

    payload = {
        "username": "KnowBetter",
        "allowed_mentions": {"parse": []},
        "embeds": [embed]
    }

    response = SESSION.post(
        WEBHOOK_URL,
        json=payload,
        timeout=20
    )

    if response.status_code not in (200, 204):
        raise RuntimeError(
            f"Discord returned HTTP {response.status_code}: "
            f"{response.text[:500]}"
        )


def main():
    if not WEBHOOK_URL:
        print(
            "ERROR: Set the DISCORD_WEBHOOK_URL "
            "environment variable before running."
        )
        return

    last_article = load_last_article()

    print("KnowBetter news bot started.")
    print(f"Checking Fox News every {CHECK_INTERVAL} seconds.")

    while True:
        try:
            article = get_latest_article()

            if article is None:
                print("No articles found.")

            else:
                article_id = get_article_id(article)

                if article_id == last_article:
                    print("No new article.")
                else:
                    post_to_discord(article)

                    # Save only after Discord confirms success.
                    save_last_article(article_id)
                    last_article = article_id

                    print(
                        "Posted successfully: "
                        + (article.get("title") or "Untitled article")
                    )

        except requests.RequestException as error:
            print(f"Network error: {error}")

        except (RuntimeError, ValueError, TypeError) as error:
            print(f"Error: {error}")

        except Exception as error:
            print(f"Unexpected error: {error}")

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
import os
import time
import html
import requests
import hashlib
import json
from pathlib import Path

# ==============================
# KnowBetter - Fox News Bot
# ==============================

WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "").strip()

RSS_URL = "https://moxie.foxnews.com/google-publisher/latest.xml"
API_URL = "https://api.rss2json.com/v1/api.json"

CHECK_INTERVAL = 300  # Check every 5 minutes
STATE_FILE = Path("knowbetter_state.json")

SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": "KnowBetterNewsBot/1.0"
})


def load_last_article():
    """Load the previously posted article ID."""
    try:
        if STATE_FILE.exists():
            data = json.loads(STATE_FILE.read_text(encoding="utf-8"))
            return data.get("last_article", "")
    except (OSError, ValueError):
        print("Warning: Could not read saved state.")

    return ""


def save_last_article(article_id):
    """Save the article ID to prevent duplicate posts."""
    try:
        STATE_FILE.write_text(
            json.dumps({"last_article": article_id}),
            encoding="utf-8"
        )
    except OSError as error:
        print(f"Warning: Could not save state: {error}")


def get_latest_article():
    """Fetch the latest article from Fox News RSS."""
    response = SESSION.get(
        API_URL,
        params={"rss_url": RSS_URL},
        timeout=20
    )
    response.raise_for_status()

    data = response.json()

    if data.get("status") != "ok":
        raise RuntimeError(
            data.get("message", "RSS2JSON returned an error.")
        )

    articles = data.get("items", [])

    if not articles:
        return None

    return articles[0]


def get_article_id(article):
    """Generate a stable ID for an article."""
    identifier = (
        article.get("guid")
        or article.get("link")
        or article.get("title")
        or ""
    )

    return hashlib.sha256(
        identifier.encode("utf-8")
    ).hexdigest()


def get_article_image(article):
    """Find the article thumbnail or enclosure image."""
    thumbnail = article.get("thumbnail", "")

    if isinstance(thumbnail, str) and thumbnail.startswith("https://"):
        return thumbnail

    enclosure = article.get("enclosure")

    if isinstance(enclosure, dict):
        image_url = enclosure.get("link", "")

        if isinstance(image_url, str) and image_url.startswith("https://"):
            return image_url

    return ""


def post_to_discord(article):
    """Send an article embed to Discord."""
    title = html.unescape(
        article.get("title") or "Latest Fox News"
    )

    description = html.unescape(
        article.get("description") or "Click to read the full article."
    )

    link = article.get("link", "")
    pub_date = article.get("pubDate", "Unknown date")
    image_url = get_article_image(article)

    # Discord embed limits
    title = title[:256]
    description = description[:4000]

    embed = {
        "title": title,
        "description": description,
        "color": 15548997,
        "footer": {
            "text": f"Fox News | {pub_date}"[:2048]
        }
    }

    if link.startswith(("https://", "http://")):
        embed["url"] = link

    if image_url:
        embed["image"] = {"url": image_url}

    payload = {
        "username": "KnowBetter",
        "allowed_mentions": {"parse": []},
        "embeds": [embed]
    }

    response = SESSION.post(
        WEBHOOK_URL,
        json=payload,
        timeout=20
    )

    if response.status_code not in (200, 204):
        raise RuntimeError(
            f"Discord returned HTTP {response.status_code}: "
            f"{response.text[:500]}"
        )


def main():
    if not WEBHOOK_URL:
        print(
            "ERROR: Set the DISCORD_WEBHOOK_URL "
            "environment variable before running."
        )
        return

    last_article = load_last_article()

    print("KnowBetter news bot started.")
    print(f"Checking Fox News every {CHECK_INTERVAL} seconds.")

    while True:
        try:
            article = get_latest_article()

            if article is None:
                print("No articles found.")

            else:
                article_id = get_article_id(article)

                if article_id == last_article:
                    print("No new article.")
                else:
                    post_to_discord(article)

                    # Save only after Discord confirms success.
                    save_last_article(article_id)
                    last_article = article_id

                    print(
                        "Posted successfully: "
                        + (article.get("title") or "Untitled article")
                    )

        except requests.RequestException as error:
            print(f"Network error: {error}")

        except (RuntimeError, ValueError, TypeError) as error:
            print(f"Error: {error}")

        except Exception as error:
            print(f"Unexpected error: {error}")

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
    
