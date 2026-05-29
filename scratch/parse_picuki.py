import re
import json

def parse_profile_file():
    with open("scratch/picuki_profile.html", "r", encoding="utf-8") as f:
        html = f.read()
        
    print("--- Parsing Picuki Profile HTML ---")
    
    # 1. Profile Name & Username
    username_match = re.search(r'<div class="profile-name">[^@]*@([^<]+)</div>', html)
    username = username_match.group(1).strip() if username_match else "Unknown"
    
    fullname_match = re.search(r'<h1 class="profile-title">([^<]+)</h1>', html)
    fullname = fullname_match.group(1).strip() if fullname_match else "Unknown"
    
    # 2. Biography
    bio_match = re.search(r'<div class="profile-description">\s*(.*?)\s*</div>', html, re.DOTALL)
    bio = bio_match.group(1).strip() if bio_match else ""
    
    # 3. Avatar
    avatar_match = re.search(r'<div class="profile-avatar"[^>]*style="background-image: url\(\'([^\']+)\'\)', html)
    avatar_url = avatar_match.group(1) if avatar_match else ""
    
    # 4. Stats
    stats = {}
    stat_matches = re.finditer(r'<li>\s*<span class="count">([^<]+)</span>\s*([^<]+)</li>', html)
    for m in stat_matches:
        val = m.group(1).strip()
        label = m.group(2).strip().lower()
        stats[label] = val
        
    print(f"Username: @{username}")
    print(f"Full Name: {fullname}")
    print(f"Bio: {bio}")
    print(f"Avatar: {avatar_url}")
    print(f"Stats: {stats}")
    
    # 5. Posts List
    # Picuki has boxes for each post: <div class="post-box"> or <div class="box-photo">
    # Let's extract post shortcodes, URLs, descriptions, images
    post_boxes = re.findall(r'<div class="box-photo">(.*?)</div>\s*</div>\s*</div>', html, re.DOTALL)
    print(f"\nExtracted {len(post_boxes)} post box chunks.")
    
    posts = []
    # Let's do a regex search for the individual items
    # Picuki structure for a post item:
    # <div class="box-photo">
    #   <a href="https://www.picuki.com/media/SHORTCODE">
    #     <img class="post-image" src="IMAGE_URL" ...>
    #   </a>
    # ...
    # <div class="photo-info">
    #   <p class="photo-description">CAPTION</p>
    # ...
    items = re.findall(r'<a href="https://www.picuki.com/media/([^"]+)"[^>]*>.*?<img[^>]*src="([^"]+)"[^>]*>.*?<p class="photo-description">([^<]*)</p>', html, re.DOTALL)
    print(f"Regex simple items found: {len(items)}")
    
    for idx, (shortcode, img_url, desc) in enumerate(items[:5]):
        print(f"\nPost {idx+1}:")
        print(f"  Shortcode: {shortcode}")
        print(f"  Image: {img_url}")
        print(f"  Description: {desc.strip()[:100]}...")

def parse_media_file():
    with open("scratch/picuki_media.html", "r", encoding="utf-8") as f:
        html = f.read()
        
    print("\n--- Parsing Picuki Media HTML ---")
    
    # 1. Author/Username
    author_match = re.search(r'<div class="profile-name">[^@]*@([^<]+)</div>', html)
    author = author_match.group(1).strip() if author_match else "Unknown"
    
    # 2. Caption/Description
    desc_match = re.search(r'<div class="post-description">\s*(.*?)\s*</div>', html, re.DOTALL)
    description = desc_match.group(1).strip() if desc_match else ""
    # Strip HTML tags from description
    clean_description = re.sub(r'<[^>]+>', '', description).strip()
    
    # 3. Image/Video URL
    # In single media page, the main image is inside <div class="single-photo"> -> <img src="IMAGE_URL" ...>
    img_match = re.search(r'<div class="single-photo"[^>]*>.*?<img[^>]*src="([^"]+)"', html, re.DOTALL)
    img_url = img_match.group(1) if img_match else ""
    
    # Check if there is a video
    is_video = "single-video" in html or "<video" in html
    
    # 4. Likes and Comments count
    likes_match = re.search(r'<span class="likes-count">([^<]+)</span>', html)
    likes = likes_match.group(1).strip() if likes_match else "0"
    
    comments_match = re.search(r'<span class="comments-count">([^<]+)</span>', html)
    comments = comments_match.group(1).strip() if comments_match else "0"
    
    print(f"Author: @{author}")
    print(f"Likes: {likes}")
    print(f"Comments: {comments}")
    print(f"Is Video: {is_video}")
    print(f"Image/Video URL: {img_url}")
    print(f"Description:\n{clean_description[:300]}...")

if __name__ == "__main__":
    parse_profile_file()
    parse_media_file()
