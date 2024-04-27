import requests

def Get(query:str,page:int=1):
    query = query.replace(' ','%20') if ' ' in query else query
    api_url = f'https://customsearch.googleapis.com/customsearch/v1?'
    params = {
        'num': 10,
        'q': query,
        'start': (page - 1) * 10 + 1,
        'key': 'Google Search API Key',
        'cx': 'Google Search API Key - cx'
    }
    headers = {
        'Accept': 'application/json',
        'compressed': ''
    }
    response = requests.get(api_url, headers=headers, params=params)
    data = response.json()
    search_items = data.get("items")

    info_dict = dict()
    for i, search_item in enumerate(search_items, start=1):

        # get the page title
        title = search_item.get("title")
        info_dict[title] = dict()

        # get domain
        displayLink = search_item.get("displayLink")
        info_dict[title]['domain'] = displayLink

        # page snippet
        snippet = search_item.get("snippet")

        # get web description
        try:
            description = search_item["pagemap"]["metatags"][0]["og:description"]
        except KeyError:
            description = snippet
        info_dict[title]['info'] = description if len(description) >= len(snippet) else snippet

        # extract the page url
        link = search_item.get("link")
        info_dict[title]['full_url'] = link

    return info_dict