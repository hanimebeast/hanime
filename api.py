
# A very simple Flask Hello World app for you to get started with...

from flask import Flask, jsonify, render_template
import requests


def jsongen(url):
    import requests
    import json
    headers = {"X-Signature-Version": "web2","X-Signature": 'aa341d8f50afb003e10a65d790b3a742f7134be4382d891aff2f751b07d3fa6e'}
    res = requests.get(url, headers=headers)
    y = json.loads(res.text)
    return y

app = Flask(__name__)

@app.route('/')
def index():
    return "hanime beast mode on!"

@app.route('/api/video/<id>', methods = ["GET"])
def video(id):
    jsondata = []
    video_api_url = "https://hanime.tv/api/v8/video?id="
    video_data_url = video_api_url + str(id)
    video_data = jsongen(video_data_url)
    streams = []
    for s in video_data['videos_manifest']['servers'][0]['streams']:
        stream_data = {'width' : s['width'],'height' : s['height'],'size_mbs' : s['filesize_mbs'],'url' : s['url']}
        streams.append(stream_data)
    json_data = {'id': video_data["hentai_video"]['id'] , 'name' : video_data["hentai_video"]['name'], 'cover_url': video_data["hentai_video"]['cover_url'], 'views' : video_data["hentai_video"]['views'], 'streams': streams}
    jsondata.append(json_data)
    return jsonify({'results': jsondata}),200

@app.route('/api/trending/<page>', methods=["GET"])
def trending(page):
    jsondata  = []
    page = page
    trending_url = "https://hanime.tv/api/v8/browse-trending?time=month&page="
    url = trending_url + str(page)
    urldata = jsongen(url)
    for x in urldata["hentai_videos"]:
        json_data = {'id': x['id'] , 'name' : x['name'], 'cover_url': x['cover_url'], 'views' : x['views'], 'link': '/video/{id}'.format(id=str(x['id']))}
        jsondata.append(json_data)

    return jsonify({'results': jsondata, 'next_page': '/trending/{page}'.format(page=str(int(page)+1))}),200



#if __name__ == "__main__":
    # serve(app, host="127.0.0.1", port=8080)
    #app.run(host="127.0.0.1", port=8080)
