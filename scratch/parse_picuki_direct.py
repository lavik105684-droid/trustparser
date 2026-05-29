import os
import subprocess
import re
import json

def fetch_and_parse_picuki_profile(username="nasa"):
    ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    url = f"https://www.picuki.com/profile/{username}"
    
    cmd = [
        "curl.exe", "-s", "-L",
        "-A", ua,
        "-H", "Accept-Language: en-US,en;q=0.9",
        "-H", "Referer: https://www.google.com/",
        url
    ]
    
    print(f"Fetching Picuki profile for @{username}...")
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore")
    html = result.stdout
    
    print(f"HTML size: {len(html)} bytes")
    if not html:
        print("Empty HTML returned.")
        return None
        
    print("--- Parsing Picuki Profile ---")
    # 1. Profile Name & Username
    username_match = re.search(r'<div class="profile-name">[^@]*@([^<]+)</div>', html)
    extracted_username = username_match.group(1).strip() if username_match else username
    
    fullname_match = re.search(r'<h1 class="profile-title">([^<]+)</h1>', html)
    fullname = fullname_match.group(1).strip() if fullname_match else username
    
    # 2. Biography
    bio_match = re.search(r'<div class="profile-description">\s*(.*?)\s*</div>', html, re.DOTALL)
    bio = bio_match.group(1).strip() if bio_match else ""
    bio = re.sub(r'<[^>]+>', '', bio).strip() # clean HTML tags
    
    # 3. Avatar
    avatar_match = re.search(r'<div class="profile-avatar"[^>]*style="background-image: url\(\'([^\']+)\'\)', html)
    avatar_url = avatar_match.group(1) if avatar_match else ""
    
    print(f"Username: @{extracted_username}")
    print(f"Full Name: {fullname}")
    print(f"Bio: {bio}")
    print(f"Avatar: {avatar_url}")
    
    # 4. Posts List
    posts = []
    # Find all post boxes
    post_boxes = re.findall(r'<div class="box-photo">(.*?)</div>\s*</div>\s*</div>', html, re.DOTALL)
    print(f"Post box chunks found: {len(post_boxes)}")
    
    # Let's extract: shortcode, thumbnail, caption, likes, comments, and date
    for idx, box in enumerate(post_boxes):
        shortcode_match = re.search(r'href="https://www.picuki.com/media/([^"]+)"', box)
        img_match = re.search(r'<img[^>]*src="([^"]+)"', box)
        desc_match = re.search(r'<p class="photo-description">\s*(.*?)\s*</p>', box, re.DOTALL)
        
        # Stats
        likes_match = re.search(r'<div class="likes">.*?([\d,km.]+)', box, re.DOTALL | re.IGNORECASE)
        comments_match = re.search(r'<div class="comments">.*?([\d,km.]+)', box, re.DOTALL | re.IGNORECASE)
        time_match = re.search(r'<div class="time">\s*([^<]+)\s*</div>', box)
        
        if shortcode_match:
            shortcode = shortcode_match.group(1).strip()
            img_url = img_match.group(1).strip() if img_match else ""
            desc = desc_match.group(1).strip() if desc_match else ""
            desc = re.sub(r'<[^>]+>', '', desc).strip()
            
            likes = likes_match.group(1).strip() if likes_match else "0"
            comments = comments_match.group(1).strip() if comments_match else "0"
            post_time = time_match.group(1).strip() if time_match else ""
            
            posts.append({
                "shortcode": shortcode,
                "url": f"https://www.instagram.com/p/{shortcode}/",
                "image_url": img_url,
                "caption": desc,
                "likes": likes,
                "comments": comments,
                "time": post_time
            })
            
    print(f"Successfully parsed {len(posts)} posts.")
    for idx, post in enumerate(posts[:3]):
        print(f"\nPost {idx+1}:")
        print(f"  Shortcode: {post['shortcode']}")
        print(f"  URL: {post['url']}")
        print(f"  Image: {post['image_url']}")
        print(f"  Caption: {post['caption'][:100]}...")
        print(f"  Likes/Comments: {post['likes']}/{post['comments']} | Time: {post['time']}")
        
    return {
        "username": extracted_username,
        "full_name": fullname,
        "biography": bio,
        "avatar_url": avatar_url,
        "posts": posts
    }

def fetch_and_parse_picuki_media(shortcode="CmYOR5Xq_OC"):
    ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    url = f"https://www.picuki.com/media/{shortcode}"
    
    cmd = [
        "curl.exe", "-s", "-L",
        "-A", ua,
        "-H", "Accept-Language: en-US,en;q=0.9",
        "-H", "Referer: https://www.google.com/",
        url
    ]
    
    print(f"\nFetching Picuki media for shortcode: {shortcode}...")
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore")
    html = result.stdout
    
    print(f"HTML size: {len(html)} bytes")
    if not html:
        print("Empty HTML returned.")
        return None
        
    print("--- Parsing Picuki Media ---")
    
    # 1. Author/Username
    author_match = re.search(r'<div class="profile-name">[^@]*@([^<]+)</div>', html)
    author = author_match.group(1).strip() if author_match else "Unknown"
    
    # 2. Caption/Description
    desc_match = re.search(r'<div class="post-description">\s*(.*?)\s*</div>', html, re.DOTALL)
    description = desc_match.group(1).strip() if desc_match else ""
    # Strip HTML tags
    clean_description = re.sub(r'<[^>]+>', '', description).strip()
    
    # 3. Image/Video URL
    img_match = re.search(r'<div class="single-photo"[^>]*>.*?<img[^>]*src="([^"]+)"', html, re.DOTALL)
    img_url = img_match.group(1) if img_match else ""
    
    # Check if video
    is_video = "single-video" in html or "<video" in html
    
    # 4. Stats
    likes_match = re.search(r'<span class="likes-count">([^<]+)</span>', html)
    likes = likes_match.group(1).strip() if likes_match else "0"
    
    comments_match = re.search(r'<span class="comments-count">([^<]+)</span>', html)
    comments = comments_match.group(1).strip() if comments_match else "0"
    
    print(f"Author: @{author}")
    print(f"Likes: {likes}")
    print(f"Comments: {comments}")
    print(f"Is Video: {is_video}")
    print(f"Image/Video URL: {img_url}")
    print(f"Description:\n{clean_description[:200]}...")
    
    return {
        "shortcode": shortcode,
        "url": f"https://www.instagram.com/p/{shortcode}/",
        "author": author,
        "caption": clean_description,
        "likes": likes,
        "comments": comments,
        "is_video": is_video,
        "media_url": img_url
    }

if __name__ == "__main__":
    fetch_and_parse_picuki_profile()
    fetch_and_parse_picuki_media()
