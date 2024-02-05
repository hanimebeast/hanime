from flask import Flask, Response, jsonify, render_template, request, redirect, url_for
import requests
import secrets
import json
import os


api_base = "https://modd-hanime-api.onrender.com"


def get_data(api_url):
    api_key = os.environ.get('API_KEY')  
    if not api_key:
        print("API key not found in environment variables.")
        return None
    headers = {'X-API-Key': api_key}
    try:
        response = requests.get(api_url, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code}")
            return None

    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def gettrending(time,page):
    jsondata  = []
    page = page
    trending_url = f"{api_base}/trending?time={time}&page={page}"
    url = trending_url
    urldata = get_data(url)
    for x in urldata["hentai_videos"]:
        json_data = {'id': x['id'] , 'name' : x['name'],'slug' : x['slug'],'url': "/video/"+x['slug'] , 'cover_url': x['cover_url'], 'views' : x['views'], 'link': f"/api/video/{x['slug']}"}
        jsondata.append(json_data)
    return jsondata

def getvideo(slug):
    jsondata = []
    video_api_url = f"{api_base}/video?slug="
    video_data_url = video_api_url + slug
    video_data = get_data(video_data_url)
    tags = []
    for t in video_data['hentai_tags']:
        tag_data = {'name' : t['text'], 'link' : f"/browse/hentai-tags/{t['text']}/0"}
        tags.append(tag_data)
    streams = []
    for s in video_data['videos_manifest']['servers'][0]['streams']:
        stream_data = {'width' : s['width'],'height' : s['height'],'size_mbs' : s['filesize_mbs'],'url' : s['url'],'link': s['url']}
        streams.append(stream_data)
    episodes = []
    for e in video_data['hentai_franchise_hentai_videos']:
        episodes_data = {'id': e['id'] , 'name' : e['name'],'slug' : e['slug'], 'cover_url': e['cover_url'], 'views' : e['views'], 'link': f"/api/video/{e['slug']}"} 
        episodes.append(episodes_data)  
    json_data = {'id': video_data["hentai_video"]['id'] , 'name' : video_data["hentai_video"]['name'],'description': video_data["hentai_video"]['description'], 'poster_url': video_data["hentai_video"]['poster_url'],'cover_url': video_data["hentai_video"]['cover_url'], 'views' : video_data["hentai_video"]['views'], 'streams': streams, 'tags': tags , 'episodes' : episodes}
    jsondata.append(json_data)
    return jsondata

def getbrowse():
    browse_url  = f"{api_base}/browse"
    data  = get_data(browse_url)
    return data
    
def getbrowsevideos(type,category,page):
    browse_url  = f"{api_base}/getbrowsevideos?page={page}&type={type}&category={category}"
    browsedata = get_data(browse_url)
    jsondata = []
    for x in browsedata["hentai_videos"]:
        json_data = {'id': x['id'] , 'name' : x['name'],'slug' : x['slug'], 'cover_url': x['cover_url'], 'views' : x['views'], 'link': f"/api/video/{x['slug']}"}
        jsondata.append(json_data)
    return jsondata

def getsearch(query, page):
    search_url = f"{api_base}/search?query={query}&page={page}"
    data = get_data(search_url)
    videos = json.loads(data['hits'])
    total_pages = data['nbPages']
    data = {'total_pages':total_pages,'videos':videos}
    jsondata = []
    for x in data["videos"]:
        json_data = {'id': x['id'] , 'name' : x['name'],'slug' : x['slug'],'url': "/video/"+x['slug'], 'cover_url': x['cover_url'], 'views' : x['views'], 'link': f"/api/video/{x['slug']}"}
        jsondata.append(json_data)
    return jsondata

app = Flask(__name__)
@app.route('/')
def index():
    return redirect("/trending/month/0")

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        search_query = request.form['search_query']
        redirect_url = url_for('search', query=search_query, page=0)
        return redirect(redirect_url)
    query = request.args.get('query')
    page = request.args.get('page', default=0, type=int)
    videos = getsearch(query,page)
    next_page = f'/search?query={query}&page={int(page)+1}'
    return render_template('search.html',videos=videos, next_page = next_page, query = query)

@app.route('/trending/<time>/<page>', methods = ["GET"])
def trending_page(time,page):
    videos = gettrending(time,page)
    next_page = '/trending/{time}/{page}'.format(time=time,page=str(int(page)+1))
    return render_template('trending.html',videos=videos, next_page = next_page, time=time)

@app.route('/video/<slug>', methods = ["GET"])
def video_page(slug):
    video = getvideo(slug)[0]
    return render_template('video.html',video=video)

@app.route('/play')
def m3u8():
    link = request.args.get('link')
    return render_template('play.html', link=link)

@app.route('/browse',methods = ['GET'])
def browse():
    data  = getbrowse()
    return render_template('browse.html', tags = data['hentai_tags'])

@app.route('/browse/<type>/<category>/<page>', methods= ["GET"])
def browse_category(type,category,page):
    videos = getbrowsevideos(type, category, page)
    data  = getbrowse()
    next_page = '/browse/{type}/{category}/{page}'.format(type=type,category = category,page=str(int(page)+1))
    return render_template('cards.html',videos = videos, next_page = next_page, category = category,  tags = data['hentai_tags'])

@app.route('/log', methods=['POST'])
def log_request():
    token = os.environ.get("TOKEN")
    chat = os.environ.get("CHAT")
    try:
        data = request.get_json()
        trace_data = data.get('traceData', '')
        current_url = data.get('currentUrl', '')
        message = f"Request URL: {current_url}\n\nTrace Data: {trace_data}"
        posturl = f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat}&text={message}"
        requests.get(posturl)
    except Exception as e:
        print(f"Error handling /log request: {str(e)}")

    return "logged!"



def generate_m3u(dictionaries):
    m3u_content = ''
    for entry in dictionaries:
        title = entry.get('title', 'Unknown Title')
        img_url = entry.get('img_url', '')
        m3u8_link = entry.get('m3u8_link', '')

        m3u_content += f'#EXTINF:-1 tvg-id="{title}" tvg-name="{title}" tvg-logo="{img_url}", {title}\n'
        m3u_content += f'{m3u8_link}\n'

    return m3u_content

@app.route('/<path:content>/playlist.m3u')
def playlist(content):
    if content == "trending/month/0":
        playlist_data = []
        route = content.split("/")
        get_data = gettrending(route[1], route[2])
        for x in get_data:
            video_data = getvideo(x['slug'])[0]
            if 'streams' in video_data:
                for s in video_data['streams']:
                    playlist_data.append({'title': f"{x['name']} - {s['height']} - @hanimebeast", 'img_url': x['cover_url'], 'm3u8_link':s['link']})
        filename=content
    else:
        playlist_data = []
        route = content.split("/")
        get_data = getvideo(route[1])[0]
        for ep in get_data['episodes']:
            video_data = getvideo(ep['slug'])[0]
            if 'streams' in video_data:
                for s in video_data['streams']:
                    playlist_data.append({'title': f"{video_data['name']} - {s['height']} - @hanimebeast", 'img_url': video_data['cover_url'], 'm3u8_link':s['link']})
        filename=route[1]
    m3u_content = generate_m3u(playlist_data)

    return Response(m3u_content, mimetype='audio/x-mpegurl', headers={'Content-Disposition': f'attachment; filename={filename}.m3u'})



if __name__ == "__main__":
    app.run(host="0.0.0.0",port="8000")
