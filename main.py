import requests as r
from bs4 import BeautifulSoup as bs
import datetime
import os
import json
import argparse

#Load the json file containing last fetch timestamps
try:
    with open('timestamp_info.json') as json_file:
        fetch_timestamp = json.load(json_file) 
except:
    fetch_timestamp = dict()

def fetch_url(url):
    """Saves all assests of the input url

    Args:
        url (string): Input URL

    Returns:
        (n_links, n_imgs, ts): Tuple of number of links, number of images and previous fetch timestamp
    """
    #Get and parse the contents of input url
    res = r.get(url)
    soup = bs(res.content,'html.parser')

    #Get links info
    links = soup.findAll('a')
    n_links = len(links)

    #Get images info
    imgs = soup.findAll('img')
    n_imgs = len(imgs)

    #Get previous fetch timestamp 
    ts = fetch_timestamp.get(url,"")
    
    #Create new directory for storing assests of url
    dir = url.split('/')[-1]
    os.makedirs(dir, exist_ok=True)

    index_html = os.path.join(dir, "index.html")

    #Info of all assets in the webpage  
    assets= soup.find_all("img", src=True) + soup.find_all("script",src=True) + soup.find_all("link",rel="stylesheet")
    
    #Iterate and save all assets to local directory 
    for asset in assets:
        try:
            src = asset['href'] if asset.name == 'link' else asset['src']
            try:
                res = r.get(src)
            except:
                res = r.get(url+src)
            
            name = src.split('/')[-1]
            if len(name.split('?v'))>1:
                name = name.split('?v')[-2]

            file_name = os.path.basename(name)
            
            file_path = os.path.join(dir, file_name)

            with open(file_path, "wb") as f:
                f.write(res.content)
            
            #update the reference to local directory path
            if asset.name == 'img'or asset.name == 'script':
                asset['src'] = file_name
            elif asset.name == 'link':
                asset['href'] = file_name
        except:
            continue

    #Save the updated html file
    with open(index_html, 'w') as f:
        f.write(str(soup))

    #Update last fetch timestamp for url
    fetch_timestamp[url] = datetime.datetime.now(datetime.timezone.utc).strftime("%a %b %d %Y %H:%M %Z")
    return n_links, n_imgs, ts 

def fetch(url_list, display_metadata=True):
    #Iterate of input urls list
    for url in url_list:
        n_links, n_imgs, ts = fetch_url(url)
        if display_metadata:
            print(f"site: {url}")
            print(f"num_links: {n_links}")
            print(f"images: {n_imgs}")
            print(f"last_fetch: {ts}")
            print('-'*100)
    #Save the timestamps info as file
    with open("timestamp_info.json", "w") as outfile:
        json.dump(fetch_timestamp, outfile)

if __name__=="__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("urls", nargs="+", help="a list of URLs to process")
    parser.add_argument("--metadata", action="store_true", help="display metadata for each URL")
    args = parser.parse_args()
    fetch(args.urls, display_metadata=args.metadata)
