import json, os, time, urllib.error, urllib.parse, urllib.request
from pathlib import Path
from flask import Flask, jsonify, send_from_directory, request

ROOT=Path(__file__).resolve().parent
STATIC=ROOT/"static"
CACHE_SECONDS=24*60*60
cache={}
COMPETITIONS={
 "WC":{"name":"FIFA World Cup","default_season":2026},
 "CL":{"name":"UEFA Champions League","default_season":2026},
 "BSA":{"name":"Campeonato Brasileiro Série A","default_season":2026},
}
app=Flask(__name__,static_folder=None)

def load_local_env():
    f=ROOT/".env"
    if f.exists():
        for raw in f.read_text(encoding="utf-8").splitlines():
            line=raw.strip()
            if line and not line.startswith("#") and "=" in line:
                k,v=line.split("=",1)
                os.environ.setdefault(k.strip(),v.strip().strip('"').strip("'"))

def fetch_standings(code,season):
    token=os.environ.get("FOOTBALL_DATA_TOKEN","").strip()
    if not token: raise RuntimeError("Configure FOOTBALL_DATA_TOKEN no arquivo .env.")
    url=f"https://api.football-data.org/v4/competitions/{code}/standings?{urllib.parse.urlencode({'season':season})}"
    req=urllib.request.Request(url,headers={"X-Auth-Token":token,"User-Agent":"FootballDashboard/1.0"})
    try:
        with urllib.request.urlopen(req,timeout=20) as r: payload=json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        if e.code in (401,403): raise RuntimeError(f"A API não autorizou esta competição/temporada (HTTP {e.code}). Seu plano pode não incluir esses dados.")
        if e.code==404: raise RuntimeError("Não há classificação disponível para esta competição/temporada.")
        if e.code==429: raise RuntimeError("Limite de requisições atingido. Tente novamente mais tarde.")
        raise RuntimeError(f"A API retornou HTTP {e.code}.")
    except urllib.error.URLError: raise RuntimeError("Não foi possível conectar à API de futebol.")
    except json.JSONDecodeError: raise RuntimeError("A API retornou uma resposta inválida.")
    groups=payload.get("standings") or []
    total=next((x for x in groups if x.get("type")=="TOTAL"),None)
    chosen=[total] if total else [x for x in groups if x.get("table")]
    rows=[]
    for group in chosen: rows.extend(group.get("table") or [])
    if not rows: raise RuntimeError("A API não disponibilizou uma tabela para esta competição.")
    return {"competition":payload.get("competition",{}).get("name",COMPETITIONS[code]["name"]),
      "season":str(payload.get("season",{}).get("startDate",season))[:4],
      "currentMatchday":payload.get("season",{}).get("currentMatchday"),"table":rows}

@app.get("/")
def index(): return send_from_directory(STATIC,"index.html")
@app.get("/<path:filename>")
def static_files(filename): return send_from_directory(STATIC,filename)
@app.get("/api/standings/<code>")
def standings(code):
    code=code.upper()
    if code not in COMPETITIONS: return jsonify({"error":"Competição não configurada."}),404
    season=request.args.get("season",str(COMPETITIONS[code]["default_season"]))
    if not season.isdigit() or len(season)!=4: return jsonify({"error":"Temporada inválida."}),400
    key=(code,season); now=time.time(); cached=cache.get(key)
    force=request.args.get("refresh")=="1"
    if cached and not force and now-cached["at"]<CACHE_SECONDS:
        return jsonify({"source":"cache","updatedAt":time.strftime("%Y-%m-%dT%H:%M:%S%z",time.localtime(cached["at"])),"data":cached["data"]})
    try:
        data=fetch_standings(code,season); cache[key]={"at":now,"data":data}
        return jsonify({"source":"api","updatedAt":time.strftime("%Y-%m-%dT%H:%M:%S%z",time.localtime(now)),"data":data})
    except RuntimeError as e:
        if cached: return jsonify({"source":"cache-stale","warning":str(e),"updatedAt":time.strftime("%Y-%m-%dT%H:%M:%S%z",time.localtime(cached["at"])),"data":cached["data"]})
        return jsonify({"error":str(e)}),502

load_local_env()
if __name__=="__main__": app.run(host="0.0.0.0",port=int(os.environ.get("PORT","8000")),debug=False)
