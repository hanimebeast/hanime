from flask import Flask, jsonify, render_template, request, redirect, url_for
import requests
import secrets
import json
from fake_useragent import UserAgent
import os



def jsongen(url):
    headers = {"X-Signature-Version": "web2","X-Signature": secrets.token_hex(32),'User-Agent': UserAgent().random}
    res = requests.get(url, headers=headers)
    y = json.loads(res.text)
    return y


def gettrending(time,page):
    jsondata  = []
    page = page
    trending_url = "https://hanime.tv/api/v8/browse-trending?time={time}&page={page}&order_by=views&ordering=desc".format(time=time,page=str(page))
    url = trending_url
    urldata = jsongen(url)
    for x in urldata["hentai_videos"]:
        json_data = {'id': x['id'] , 'name' : x['name'],'slug' : x['slug'],'url': "/video/"+x['slug'] , 'cover_url': x['cover_url'], 'views' : x['views'], 'link': f"/api/video/{x['slug']}"}
        jsondata.append(json_data)
    return jsondata

def getvideo(slug):
    jsondata = []
    video_api_url = "https://hanime.tv/api/v8/video?id="
    video_data_url = video_api_url + slug
    video_data = jsongen(video_data_url)
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
    browse_url  = "https://hanime.tv/api/v8/browse"
    data  = jsongen(browse_url)
    return data
    
def getbrowsevideos(type,category,page):
    browse_url  = f"https://hanime.tv/api/v8/browse/{type}/{category}?page={page}&order_by=views&ordering=desc"
    browsedata = jsongen(browse_url)
    jsondata = []
    for x in browsedata["hentai_videos"]:
        json_data = {'id': x['id'] , 'name' : x['name'],'slug' : x['slug'], 'cover_url': x['cover_url'], 'views' : x['views'], 'link': f"/api/video/{x['slug']}"}
        jsondata.append(json_data)
    return jsondata


app = Flask(__name__)
@app.route('/')
def index():
    return redirect("/trending/month/0")

@app.route('/api')
def api():
    return render_template('api.html')

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


# api
@app.route('/api/video/<slug>', methods = ["GET"])
def video_api(slug):
    jsondata = getvideo(slug)
    return jsonify({'results': jsondata}),200

@app.route('/api/trending/<time>/<page>', methods=["GET"])
def trending_api(time, page):
    jsondata = gettrending(time,page)
    return jsonify({'results': jsondata, 'next_page': '/api/trending/{time}/{page}'.format(time=time,page=str(int(page)+1))}),200

@app.route('/api/browse/<type>',methods = ["GET"])
def browse_type_api(type):
    data = getbrowse()
    jsondata = data[type]
    if type == 'hentai_tags':
        for x in data[type]:
            x.update({'url' : f"/api/browse/hentai-tags/{x['text']}/0"})
    elif type == 'brands':
        for x in data[type]:
            x.update({'url' : f"/api/browse/brands/{x['slug']}/0"})
    return jsonify({'results': jsondata}),200

@app.route('/api/browse',methods = ["GET"])
def browse_api():
    return jsonify({'tags' : '/api/browse/hentai_tags','brands' : '/api/browse/brands'}),200

@app.route('/api/browse/<type>/<category>/<page>',methods=["GET"])
def browse_category_api(type,category,page):
    data = getbrowsevideos(type,category,page)
    return jsonify({'results': data, 'next_page': '/api/browse/{type}/{category}/{page}'.format(type=type,category = category,page=str(int(page)+1))}),200


#log

@app.route('/log',methods=["GET"])
def log():
    ip = request.args.get("ip")
    route = request.args.get("r")
    token = os.environ.get("TOKEN")
    chat = os.environ.get("CHAT")
    url = f"http://ip-api.com/json/{ip}"
    data = f"route:{route}\n{str(jsongen(url))}"
    posturl = f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat}&text={data}"
    try:
        requests.get(posturl)
    except:
        pass
    return "logged!"









if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080,debug=True)
