import json
import os
import urllib.error
import urllib.parse
import urllib.request

from flask import Flask, jsonify, request

app = Flask(__name__)

PAGE = r'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>YouTube Finder</title>
<style>
:root{--bg:#0f1115;--card:#171a21;--line:#262b36;--text:#e8eaf0;--mute:#98a1b3;--acc:#ff4d4d;--acc2:#3b82f6}
@media (prefers-color-scheme:light){:root{--bg:#f5f6f8;--card:#fff;--line:#e2e5ea;--text:#14171c;--mute:#5d6676}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font:15px/1.45 system-ui,Segoe UI,Roboto,sans-serif}
header{padding:20px 16px 8px;max-width:1100px;margin:0 auto}h1{margin:0;font-size:22px}h1 span{color:var(--acc)}
.sub{color:var(--mute);margin:2px 0 0;font-size:13px}
main{max-width:1100px;margin:0 auto;padding:8px 16px 48px}
.tabs{display:flex;gap:8px;margin:12px 0}
.tab{border:1px solid var(--line);background:var(--card);color:var(--text);padding:8px 16px;border-radius:999px;cursor:pointer;font:inherit}
.tab.on{background:var(--acc);border-color:var(--acc);color:#fff}
.bar{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:12px}
input,select{background:var(--card);color:var(--text);border:1px solid var(--line);border-radius:10px;padding:10px 12px;font:inherit}
input[type=search]{flex:1 1 260px;min-width:0}
button.go{background:var(--acc2);border:0;color:#fff;border-radius:10px;padding:10px 18px;font:inherit;cursor:pointer}
button.ghost{background:transparent;border:1px solid var(--line);color:var(--text);border-radius:8px;padding:6px 10px;font:inherit;font-size:13px;cursor:pointer}
.tools{display:flex;gap:8px;align-items:center;margin:6px 0 12px;color:var(--mute);font-size:13px;min-height:30px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:14px}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;overflow:hidden;display:flex;flex-direction:column}
.card img{width:100%;aspect-ratio:16/9;object-fit:cover;background:#000;display:block}
.cb{padding:10px 12px;display:flex;flex-direction:column;gap:6px;flex:1}
.t{font-weight:600;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.m{color:var(--mute);font-size:12.5px}.st{display:flex;gap:10px;font-size:12.5px;color:var(--mute)}
.ac{display:flex;gap:6px;margin-top:auto;padding-top:4px}.ac a{text-decoration:none}
.msg{padding:14px;border:1px solid var(--line);border-radius:10px;background:var(--card)}.err{border-color:var(--acc);color:var(--acc)}
</style></head><body>
<header><h1><span>▶</span> YouTube Finder</h1><p class="sub">Search videos or see what's trending. Public YouTube data only.</p></header>
<main>
<div class="tabs"><button class="tab on" data-m="search">Search</button><button class="tab" data-m="trending">Trending</button></div>
<form class="bar" id="f">
<input type="search" id="q" placeholder="Search e.g. software testing automation" autocomplete="off">
<select id="order"><option value="relevance">Most relevant</option><option value="date">Newest</option><option value="viewCount">Most viewed</option></select>
<select id="region" hidden><option value="PK">Pakistan</option><option value="US">United States</option><option value="IN">India</option><option value="GB">United Kingdom</option><option value="AE">UAE</option><option value="CA">Canada</option><option value="AU">Australia</option></select>
<select id="n"><option>10</option><option>20</option><option>30</option><option>50</option></select>
<button class="go" type="submit">Go</button>
</form>
<div class="tools" id="tools"></div>
<div id="out"></div>
</main>
<script>
const $=s=>document.querySelector(s);let mode='search',rows=[];
const fmt=n=>n==null?'':Intl.NumberFormat('en',{notation:'compact'}).format(n);
function setMode(m){mode=m;document.querySelectorAll('.tab').forEach(t=>t.classList.toggle('on',t.dataset.m===m));
$('#q').hidden=$('#order').hidden=m!=='search';$('#region').hidden=m!=='trending';load()}
document.querySelectorAll('.tab').forEach(t=>t.onclick=()=>setMode(t.dataset.m));
$('#f').onsubmit=e=>{e.preventDefault();load()};
function msg(t,err){const d=document.createElement('div');d.className='msg'+(err?' err':'');d.textContent=t;$('#out').replaceChildren(d);$('#tools').replaceChildren()}
async function load(){
 let url;
 if(mode==='search'){const q=$('#q').value.trim();if(!q){msg('Type something to search.');return}
  url='/search?q='+encodeURIComponent(q)+'&order='+$('#order').value+'&max_results='+$('#n').value}
 else url='/trending?region='+$('#region').value+'&max_results='+$('#n').value;
 msg('Loading…');
 try{const r=await fetch(url);const d=await r.json();if(!r.ok){msg(d.error||'Request failed',true);return}
  rows=d.videos||[];render()}catch(e){msg('Network error: '+e.message,true)}}
function el(tag,cls,text){const e=document.createElement(tag);if(cls)e.className=cls;if(text!=null)e.textContent=text;return e}
function render(){
 const out=$('#out'),tools=$('#tools');
 if(!rows.length){msg('No results.');return}
 const g=el('div','grid');
 rows.forEach(v=>{const c=el('div','card');const a=document.createElement('a');a.href=v.url;a.target='_blank';a.rel='noopener';
  const im=document.createElement('img');im.src=v.thumbnail||'';im.alt='';im.loading='lazy';a.append(im);c.append(a);
  const b=el('div','cb');b.append(el('div','t',v.title||''));
  b.append(el('div','m',(v.channel||'')+(v.published?' · '+new Date(v.published).toLocaleDateString():'')));
  if(v.views!=null){const s=el('div','st');s.append(el('span',null,fmt(v.views)+' views'),el('span',null,fmt(v.likes)+' likes'),el('span',null,fmt(v.comments)+' comments'));b.append(s)}
  const ac=el('div','ac');const o=el('a');o.href=v.url;o.target='_blank';o.rel='noopener';const ob=el('button','ghost','Open');ob.type='button';o.append(ob);
  const cp=el('button','ghost','Copy link');cp.type='button';cp.onclick=()=>{navigator.clipboard.writeText(v.url);cp.textContent='Copied';setTimeout(()=>cp.textContent='Copy link',1200)};
  ac.append(o,cp);b.append(ac);c.append(b);g.append(c)});
 out.replaceChildren(g);
 tools.replaceChildren(el('span',null,rows.length+' videos'),btn('Export CSV',csv),btn('Export JSON',json))}
function btn(t,f){const b=el('button','ghost',t);b.type='button';b.onclick=f;return b}
function save(name,type,data){const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([data],{type}));a.download=name;a.click()}
function json(){save('videos.json','application/json',JSON.stringify(rows,null,2))}
function csv(){const cols=['id','title','channel','published','views','likes','comments','url'];
 const e=x=>'"'+String(x==null?'':x).replace(/"/g,'""')+'"';
 save('videos.csv','text/csv',[cols.join(',')].concat(rows.map(r=>cols.map(c=>e(r[c])).join(','))).join('\n'))}
msg('Type something to search, or open Trending.');
</script></body></html>
'''


@app.get("/")
def home():
    return PAGE, 200, {"Content-Type": "text/html; charset=utf-8"}

BASE = "https://www.googleapis.com/youtube/v3"


def yt(path, **params):
    key = os.environ.get("YOUTUBE_API_KEY")
    if not key:
        return None, ("YOUTUBE_API_KEY is not set on this deployment", 500)
    params["key"] = key
    url = f"{BASE}/{path}?{urllib.parse.urlencode(params)}"
    try:
        with urllib.request.urlopen(url, timeout=15) as r:
            return json.load(r), None
    except urllib.error.HTTPError as e:
        try:
            msg = json.load(e).get("error", {}).get("message", e.reason)
        except Exception:
            msg = str(e.reason)
        return None, (msg, e.code)
    except Exception as e:  # network or timeout
        return None, (str(e), 502)


def fail(err):
    return jsonify({"error": err[0]}), err[1]


def limit():
    n = request.args.get("max_results", 10, type=int)
    return n if 1 <= n <= 50 else 10


def card(item, vid):
    s = item.get("snippet", {})
    return {
        "id": vid,
        "title": s.get("title"),
        "channel": s.get("channelTitle"),
        "channel_id": s.get("channelId"),
        "published": s.get("publishedAt"),
        "thumbnail": (s.get("thumbnails", {}).get("high") or {}).get("url"),
        "url": f"https://www.youtube.com/watch?v={vid}",
    }


@app.get("/info")
def info():
    return jsonify({
        "name": "YouTube API Tool",
        "endpoints": {
            "/search": "q, max_results (1-50), order (relevance|date|viewCount)",
            "/trending": "region (US, IN, PK...), max_results (1-50), category (optional id)",
            "/video": "video_id",
            "/channel": "channel_id",
        },
        "configured": bool(os.environ.get("YOUTUBE_API_KEY")),
    })


@app.get("/search")
def search():
    q = request.args.get("q")
    if not q:
        return jsonify({"error": "Missing 'q' parameter"}), 400
    order = request.args.get("order", "relevance")
    if order not in ("relevance", "date", "viewCount", "rating"):
        order = "relevance"
    data, err = yt("search", q=q, part="snippet", type="video", maxResults=limit(), order=order)
    if err:
        return fail(err)
    items = [card(i, i["id"]["videoId"]) for i in data.get("items", []) if i.get("id", {}).get("videoId")]
    return jsonify({"count": len(items), "videos": items})


@app.get("/trending")
def trending():
    params = dict(part="snippet,statistics", chart="mostPopular",
                  regionCode=request.args.get("region", "US"), maxResults=limit())
    if request.args.get("category"):
        params["videoCategoryId"] = request.args["category"]
    data, err = yt("videos", **params)
    if err:
        return fail(err)
    out = []
    for i in data.get("items", []):
        c = card(i, i["id"])
        st = i.get("statistics", {})
        c.update(views=int(st.get("viewCount", 0)), likes=int(st.get("likeCount", 0)),
                 comments=int(st.get("commentCount", 0)))
        out.append(c)
    return jsonify({"count": len(out), "videos": out})


@app.get("/video")
def video():
    vid = request.args.get("video_id")
    if not vid:
        return jsonify({"error": "Missing 'video_id' parameter"}), 400
    data, err = yt("videos", part="snippet,statistics,contentDetails", id=vid)
    if err:
        return fail(err)
    items = data.get("items", [])
    if not items:
        return jsonify({"error": "Video not found"}), 404
    i = items[0]
    c = card(i, vid)
    st = i.get("statistics", {})
    c.update(description=i["snippet"].get("description"), duration=i["contentDetails"].get("duration"),
             views=int(st.get("viewCount", 0)), likes=int(st.get("likeCount", 0)),
             comments=int(st.get("commentCount", 0)), tags=i["snippet"].get("tags", []))
    return jsonify(c)


@app.get("/channel")
def channel():
    cid = request.args.get("channel_id")
    if not cid:
        return jsonify({"error": "Missing 'channel_id' parameter"}), 400
    data, err = yt("channels", part="snippet,statistics", id=cid)
    if err:
        return fail(err)
    items = data.get("items", [])
    if not items:
        return jsonify({"error": "Channel not found"}), 404
    i = items[0]
    st = i.get("statistics", {})
    return jsonify({
        "id": cid, "title": i["snippet"].get("title"), "description": i["snippet"].get("description"),
        "subscribers": int(st.get("subscriberCount", 0)), "videos": int(st.get("videoCount", 0)),
        "views": int(st.get("viewCount", 0)), "url": f"https://www.youtube.com/channel/{cid}",
    })
