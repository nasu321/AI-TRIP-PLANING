import urllib.request, json, urllib.parse, os

def get_wiki_image(query):
    try:
        q = urllib.parse.quote(query)
        url = f'https://en.wikipedia.org/w/api.php?action=query&prop=pageimages&format=json&piprop=original&titles={q}'
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(req)
        data = json.loads(response.read())
        pages = data['query']['pages']
        for page_id in pages:
            if 'original' in pages[page_id]:
                return pages[page_id]['original']['source']
    except Exception as e:
        pass
    return None

places = [
    "Hôtel Le Marais", "Montmartre", "Palais Garnier", "Eiffel Tower",
    "Ubud", "Seminyak", "Uluwatu Temple", "Canggu",
    "Shinjuku", "Sensō-ji", "Shibuya Crossing", "Akihabara",
    "Burj Khalifa", "Dubai Marina", "Dubai Creek", "Palm Jumeirah",
    "Covent Garden", "Tower Bridge", "Notting Hill", "Mayfair",
    "Louvre Museum", "Notre-Dame de Paris", "Palace of Versailles",
    "Ubud Monkey Forest", "Tegallalang Rice Terrace", "Seminyak Beach", "Mount Batur",
    "Tokyo Skytree", "Meiji Shrine", "Tsukiji Outer Market", 
    "Dubai Mall",
    "British Museum", "Tower of London", "Buckingham Palace", "Camden Market", "Hyde Park",
    "Taj Mahal"
]

cache = {}
for p in places:
    img = get_wiki_image(p)
    if img:
        cache[p] = img
        print(f"Found: {p} -> {img}")
    else:
        # Fallback to a broader search or generic query
        fallback = p.split()[-1]
        img2 = get_wiki_image(fallback)
        if img2:
            cache[p] = img2
            print(f"Fallback Found: {p} -> {img2}")
        else:
            cache[p] = f"https://picsum.photos/seed/{abs(hash(p))}/800/500"
            print(f"Not found: {p}")

with open("image_cache.json", "w") as f:
    json.dump(cache, f, indent=4)
