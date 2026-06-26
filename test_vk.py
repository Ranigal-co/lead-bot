from src.vk_search import search_vk_posts
from src.config import VK_KEYWORDS, CITIES

def test_vk():
    print(f"Keywords: {VK_KEYWORDS}")
    print(f"Cities: {CITIES}")
    
    query = f"{VK_KEYWORDS[0]} {CITIES[0]}"
    print(f"Testing query: {query}")
    
    posts = search_vk_posts(query, limit=5)
    
    if not posts:
        print("No posts found.")
    else:
        print(f"Found {len(posts)} posts:")
        for post in posts:
            print(f"- {post['text'][:100]}...")

if __name__ == "__main__":
    test_vk()