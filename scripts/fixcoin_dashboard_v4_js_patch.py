#!/usr/bin/env python3
from pathlib import Path

JS=Path('/app/monitor/static/dashboard_v4.js')
text=JS.read_text()
repls={
"function render(s){lastStatus=s;":"function render(s,animate=false){lastStatus=s;",
"$('uptime').textContent=duration((Number(s.ts)||Date.now()/1000)-parseTime(s.started_at||0)||((Date.now()-uptimeStart)/1000));":"$('uptime').textContent=duration((Date.now()-uptimeStart)/1000);",
"if(valid>lastAccepted){":"if(animate&&valid>lastAccepted){",
"if(bad>lastRejected){":"if(animate&&bad>lastRejected){",
"if(progress>=100){flashClass($('candidate'),'explode');if(progress>100)progress=100}":"if(animate&&progress>=100){flashClass($('candidate'),'explode');if(progress>100)progress=100}",
"if(r.ok)render(await r.json())":"if(r.ok)render(await r.json(),false)",
}
for old,new in repls.items():
    if old not in text:
        raise RuntimeError(f'missing dashboard v4 patch anchor: {old[:70]}')
    text=text.replace(old,new,1)
JS.write_text(text)
print('patched dashboard v4 JS: SSE owns effects, polling stays authoritative')
