import os
import re
import json
import requests
from urllib.parse import urlparse, parse_qs

def load_settings():
    settings_path = "settings.json"
    if os.path.exists(settings_path):
        with open(settings_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"save_path": os.path.join(os.path.expanduser("~"), "Desktop", "knowunity-downloads")}

def extract_id(url):
    url = url.split('?')[0]
    match = re.search(r'/knows/(\w{8}-\w{4}-\w{4}-\w{4}-\w{12})', url)
    return match.group(1) if match else None

def download_file(url, folder, filename):
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        filepath = os.path.join(folder, filename)
        with open(filepath, 'wb') as file:
            for chunk in response.iter_content(chunk_size=1024):
                file.write(chunk)
        print(f"Downloaded: {filepath}")
    else:
        print(f"ERROR: I can't download this: {url}")

def save_metadata(folder, data):
    metadata_path = os.path.join(folder, "metadata.json")
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"Succesfully saved metadata!")

def main():
    settings = load_settings()
    save_path = settings.get("save_path", os.path.join(os.path.expanduser("~"), "Desktop", "knowunity-downloads"))
    
    print("""
██╗  ██╗███╗   ██╗ ██████╗ ██╗    ██╗██╗   ██╗███╗   ██╗██╗████████╗██╗   ██╗
██║ ██╔╝████╗  ██║██╔═══██╗██║    ██║██║   ██║████╗  ██║██║╚══██╔══╝╚██╗ ██╔╝
█████╔╝ ██╔██╗ ██║██║   ██║██║ █╗ ██║██║   ██║██╔██╗ ██║██║   ██║    ╚████╔╝ 
██╔═██╗ ██║╚██╗██║██║   ██║██║███╗██║██║   ██║██║╚██╗██║██║   ██║     ╚██╔╝  
██║  ██╗██║ ╚████║╚██████╔╝╚███╔███╔╝╚██████╔╝██║ ╚████║██║   ██║      ██║   
╚═╝  ╚═╝╚═╝  ╚═══╝ ╚═════╝  ╚══╝╚══╝  ╚═════╝ ╚═╝  ╚═══╝╚═╝   ╚═╝      ╚═╝   

KnowUnity Downloader by Irylek
https://github.com/Irylek/KnowUnity-Downloader/
    """)
    
    while True:
        url = input("URL: ")
        print()
        if url.lower() == 'exit':
            print("Closing..")
            break
        
        note_id = extract_id(url)
        
        if not note_id:
            print("ERROR: I didn't found the ID in the URL you provided :(")
            print()
            continue
        
        api_url = f"https://apiedge-eu-central-1.knowunity.com/knows/{note_id}/seo"
        headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'pl,en;q=0.9',
            'origin': 'https://knowunity.pl',
            'referer': 'https://knowunity.pl/',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',
            'x-interface-language': 'pl',
            'x-platform': 'web'
        }
        
        response = requests.get(api_url, headers=headers)
        
        if response.status_code != 200:
            print("ERROR: I didn't got the API response... Check if you have internet connection.")
            print()
            continue
        
        data = response.json()
        know = data.get("know", {})
        documents = know.get("documents", [])
        pages = know.get("knowDocumentPages", [])
        
        if not documents:
            print("ERROR: I didn't found any PDF files...")
            print()
            continue
        
        folder_path = os.path.join(save_path, note_id)
        pdf_folder = os.path.join(folder_path, "pdf")
        photos_folder = os.path.join(folder_path, "photos")
        
        os.makedirs(pdf_folder, exist_ok=True)
        os.makedirs(photos_folder, exist_ok=True)
        
        pdf_url = documents[0].get("contentUrl")
        if pdf_url:
            download_file(pdf_url, pdf_folder, "document.pdf")
        
        for page in pages:
            image_url = page.get("imageUrl")
            page_number = page.get("pageNumber", 1)
            if image_url:
                download_file(image_url, photos_folder, f"{page_number}.webp")
        
        metadata = {
            "creator": know.get("knower", {}).get("user", {}).get("username", "Unknown"),
            "originalTitle": know.get("title", "Unknown"),
            "description": know.get("description", ""),
            "slug": know.get("slug", ""),
            "savesCount": know.get("savesCount", 0),
            "commentsCount": know.get("commentsCount", 0),
            "publishedOn": know.get("publishedOn", "Unknown"),
            "views": know.get("views", 0)
        }
        save_metadata(folder_path, metadata)
        print()
        print("Successfully downloaded everything! If you didn't set up settings.json,")
        print("you can find your downloaded files on the desktop!")
        print()
    
if __name__ == "__main__":
    main()
