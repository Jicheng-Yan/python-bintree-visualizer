from __future__ import annotations
from dataclasses import dataclass
from typing import Any, List, Optional
import json
import time
import os
from .bst import BinarySearchTree

@dataclass
class Snapshot:
    ts: float
    op: str
    key: Any
    tree: Any
    note: Optional[str] = None

class VisualDebugger:
    """Record snapshots of a tree after each operation and export an HTML visualizer."""

    def __init__(self, out_dir: str = "visual") -> None:
        self.out_dir = out_dir
        self.snapshots: List[Snapshot] = []
        os.makedirs(out_dir, exist_ok=True)

    def record(self, op: str, key: Any, tree: BinarySearchTree, note: Optional[str] = None) -> None:
        self.snapshots.append(
            Snapshot(time.time(), op, key, tree.to_dict(), note)
        )

    def clear(self) -> None:
        self.snapshots.clear()

    def export(self, filename: str = "index.html") -> str:
        html_path = os.path.join(self.out_dir, filename)
        data_path = os.path.join(self.out_dir, "trace.json")
        with open(data_path, "w", encoding="utf-8") as f:
            json.dump([s.__dict__ for s in self.snapshots], f)
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(self._html_template())
        return html_path

    def _html_template(self) -> str:
        # Minimal interactive viewer using vanilla JS and SVG
        return """<!DOCTYPE html>
<html lang=\"en\">
<head>
<meta charset=\"utf-8\"/>
<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\"/>
<title>BST Visual Debugger</title>
<style>
body{font-family:system-ui,Arial,sans-serif;margin:0;display:flex;min-height:100vh}
#sidebar{width:320px;border-right:1px solid #ddd;overflow:auto}
#main{flex:1;display:flex;flex-direction:column}
#toolbar{padding:8px;border-bottom:1px solid #ddd;display:flex;gap:8px;align-items:center}
#canvas{flex:1;overflow:auto;background:#fafafa}
button{padding:6px 10px}
.snap{padding:8px;border-bottom:1px solid #eee;cursor:pointer}
.snap.active{background:#f0f7ff}
.node{fill:#fff;stroke:#333}
.link{stroke:#aaa}
text{font-size:12px;dominant-baseline:middle;text-anchor:middle}
</style>
</head>
<body>
<div id=\"sidebar\"></div>
<div id=\"main\">
  <div id=\"toolbar\">
    <button id=\"prev\">Prev</button>
    <button id=\"next\">Next</button>
    <span id=\"info\"></span>
  </div>
  <div id=\"canvas\">
    <svg id=\"svg\" width=\"2000\" height=\"1200\"></svg>
  </div>
</div>
<script>
async function loadTrace(){
  const res = await fetch('trace.json');
  return await res.json();
}
function layoutTree(node,x,y,dx,arr){
  if(!node) return;
  const here={x,y,key:node.key};
  arr.push(here);
  if(node.left){
    arr.push({x1:x,y1:y,x2:x-dx,y2:y+80,link:true});
    layoutTree(node.left,x-dx,y+80,dx/1.8,arr);
  }
  if(node.right){
    arr.push({x1:x,y1:y,x2:x+dx,y2:y+80,link:true});
    layoutTree(node.right,x+dx,y+80,dx/1.8,arr);
  }
}
function render(tree){
  const svg=document.getElementById('svg');
  svg.innerHTML='';
  const elems=[]; layoutTree(tree,1000,60,360,elems);
  for(const e of elems){
    if(e.link){
      const l=document.createElementNS('http://www.w3.org/2000/svg','line');
      l.setAttribute('x1',e.x1);l.setAttribute('y1',e.y1);
      l.setAttribute('x2',e.x2);l.setAttribute('y2',e.y2);
      l.setAttribute('class','link');
      svg.appendChild(l);
    }
  }
  for(const e of elems){
    if(!e.link){
      const g=document.createElementNS('http://www.w3.org/2000/svg','g');
      const c=document.createElementNS('http://www.w3.org/2000/svg','circle');
      c.setAttribute('cx',e.x);c.setAttribute('cy',e.y);c.setAttribute('r',18);
      c.setAttribute('class','node');
      const t=document.createElementNS('http://www.w3.org/2000/svg','text');
      t.setAttribute('x',e.x);t.setAttribute('y',e.y);
      t.textContent=e.key;
      g.appendChild(c);g.appendChild(t);svg.appendChild(g);
    }
  }
}
function sidebarItem(s,i){
  const d=document.createElement('div');
  d.className='snap';
  d.textContent=`${i+1}. ${s.op}(${s.key}) ${s.note? ' - '+s.note:''}`;
  d.onclick=()=>select(i);
  return d;
}
let trace=[], idx=0;
function select(i){
  idx=i; update();
}
function update(){
  [...document.querySelectorAll('.snap')].forEach((el,i)=>{
    if(i===idx) el.classList.add('active'); else el.classList.remove('active');
  });
  const s=trace[idx];
  document.getElementById('info').textContent = `${idx+1}/${trace.length} - ${s.op}(${s.key})`;
  render(s.tree);
}
(async ()=>{
  trace = await loadTrace();
  const sb=document.getElementById('sidebar');
  trace.forEach((s,i)=> sb.appendChild(sidebarItem(s,i)) );
  document.getElementById('prev').onclick=()=>{ if(idx>0) select(idx-1); };
  document.getElementById('next').onclick=()=>{ if(idx<trace.length-1) select(idx+1); };
  select(0);
})();
</script>
</body>
</html>"""
