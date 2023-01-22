
# A very simple Flask Hello World app for you to get started with...

from flask import Flask, jsonify, render_template
import requests
import secrets

def jsongen(url):
    import requests
    import json
    headers = {"X-Signature-Version": "web2","X-Signature": secrets.token_hex(32)}
    res = requests.get(url, headers=headers)
    y = json.loads(res.text)
    return y

app = Flask(__name__)

@app.route('/')
def index():
    return "hanime beast mode on!"

@app.route('/trending/<page>', methods=["GET"])
def trending(page):
    jsondata  = []
    page = page
    video_api_url = "https://hanime.tv/api/v8/video?id="
    trending_url = "https://hanime.tv/api/v8/browse-trending?time=month&page="
    url = trending_url + str(page)
    urldata = jsongen(url)
    for x in urldata["hentai_videos"]:
        video_data_url = video_api_url + str(x['id'])
        video_data = jsongen(video_data_url)
        streams = []
        for s in video_data['videos_manifest']['servers'][0]['streams']:
            stream_data = {'width' : s['width'],'height' : s['height'],'size_mbs' : s['filesize_mbs'],'url' : s['url']}
            streams.append(stream_data)
        json_data = {'id': x['id'] , 'name' : x['name'], 'cover_url': x['cover_url'], 'views' : x['views'], 'streams': streams}
        jsondata.append(json_data)

    return jsonify({'results': jsondata, 'page': page}),200


#if __name__ == "__main__":
    # serve(app, host="127.0.0.1", port=8080)
    #app.run(host="127.0.0.1", port=8080)
