import fs from 'fs'; import * as d3 from 'd3-geo'; import * as topo from 'topojson-client';
const us=JSON.parse(fs.readFileSync('node_modules/us-atlas/states-10m.json'));
const usStates=topo.feature(us,us.objects.states).features;
const w50=JSON.parse(fs.readFileSync('node_modules/world-atlas/countries-50m.json'));
const world=topo.feature(w50,w50.objects.countries).features;
const W=640,H=480,r=v=>Math.round(v*10)/10;
for (const f of process.argv.slice(2)){
  const R=JSON.parse(fs.readFileSync(f));
  const states=R.country==='usa'?usStates:world;
  const lines=R.tracks;
  const proj=d3.geoConicEqualArea().parallels([30,45]).rotate([96,0]);
  const mp={type:'MultiLineString',coordinates:lines};
  const c=d3.geoCentroid(mp); proj.rotate([-c[0],0]).parallels([c[1]-4,c[1]+4]);
  proj.fitExtent([[60,50],[W-60,H-50]],mp);
  proj.clipExtent([[-20,-20],[W+20,H+20]]);
  const path=d3.geoPath(proj);
  const st=states.filter(s=>{const b=path.bounds(s);return b[1][0]>0&&b[0][0]<W&&b[1][1]>0&&b[0][1]<H;})
    .map(s=>`<path class="rm-state" d="${(path(s)||'').replace(/-?\d+\.\d+/g,m=>Math.round(+m))}"/>`).join('');
  const tr=lines.map(l=>`<path class="rm-route rm-track" d="${'M'+l.map(p=>proj(p).map(Math.round).join(',')).join('L')}"/>`).join('');
  // states touched
  const touched=new Set();
  for(const l of lines) for(let i=0;i<l.length;i+=(R.country==='usa'?1:3)){for(const s of states){if(d3.geoContains(s,l[i])){touched.add(s.properties.name);break;}}}
  R.states=[...touched];
  // endpoints
  const ends=[]; for(const d of R.days){for(const n of [d.from,d.to]) if(!ends.includes(n)) ends.push(n);}
  let dots='',labels='',placed=[],rects=[];
  for(const n of ends){const p=R.points[n]; if(!p) continue; const [x,y]=proj(p).map(r);
    if(placed.some(([a,b])=>Math.hypot(a-x,b-y)<10)) continue; placed.push([x,y]);
    const lab=(R.maplabels&&R.maplabels[n])||n.replace(/^(Best Western|Hyatt Place|Hampton Inn & Suites|EagleRider|The Lodge at|Element|Balch Hotel,|The Williams Inn,|Redfish Riverside Inn,|Smoky Mountain Harley-Davidson,|Patriot Harley-Davidson,|Grizzly Harley-Davidson,|Big Sky Motorsports,|Sheridan \/ Big Horn Mountains KOA)\s*/,'').split(', ').filter(x=>x.length>2)[0]||n;
    let right=x<W*0.62; const w=lab.length*8.2+4;
    const box=rt=>rt?[x+8,y-9,x+8+w,y+7]:[x-8-w,y-9,x-8,y+7];
    const hit=b=>rects.some(q=>!(b[2]<q[0]||b[0]>q[2]||b[3]<q[1]||b[1]>q[3]));
    let dy=0;
    if(hit(box(right))){ if(!hit(box(!right))) right=!right; else dy=16; }
    const bb=box(right); bb[1]+=dy; bb[3]+=dy; rects.push(bb);
    dots+=`<circle class="rm-stop" cx="${x}" cy="${y}" r="5.5"/>`;
    labels+=`<text class="rm-label" x="${right?x+10:x-10}" y="${y+5+dy}" text-anchor="${right?'start':'end'}">${lab}</text>`;}
  for(const n of (R.marks||[])){const p=R.points[n]; if(!p||ends.includes(n)) continue; const [x,y]=proj(p).map(r); const right=x<W*0.62; const lab=(R.maplabels&&R.maplabels[n])||n.replace(/, [A-Z]{2}$/,'');
    dots+=`<circle class="rm-mark" cx="${x}" cy="${y}" r="4.5"/>`; labels+=`<text class="rm-label rm-label-s" x="${right?x+10:x-10}" y="${y+4}" text-anchor="${right?'start':'end'}">${lab}</text>`;}
  const svg=`<svg class="routemap" viewBox="0 0 ${W} ${H}" role="img" aria-label="Route map"><defs><clipPath id="rmclip"><rect width="${W}" height="${H}" rx="10"/></clipPath></defs><g clip-path="url(#rmclip)"><rect class="rm-bg" width="${W}" height="${H}"/>${st}</g>${tr}${dots}${labels}</svg>`;
  fs.writeFileSync(f.replace('.json','.map.svg'),svg);
  fs.writeFileSync(f,JSON.stringify(R));
  console.log(f.split('/').pop(), svg.length, R.states.join(', '));
}
