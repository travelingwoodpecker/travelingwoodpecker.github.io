import fs from 'fs'; import * as d3 from 'd3-geo'; import * as topo from 'topojson-client';
const us=JSON.parse(fs.readFileSync('node_modules/us-atlas/states-10m.json'));
const states=topo.feature(us,us.objects.states).features;
const w50=JSON.parse(fs.readFileSync('node_modules/world-atlas/countries-50m.json'));
const countries=topo.feature(w50,w50.objects.countries).features;
const W=640,H=480,r=v=>Math.round(v*10)/10;
for (const f of process.argv.slice(2)){
  const R=JSON.parse(fs.readFileSync(f));
  const P=Object.fromEntries(R.route.concat(R.overnights).map(n=>[n,null]));
  const all=JSON.parse(fs.readFileSync('pts.json'));
  const coords=R.route.map(n=>all[n]);
  const lon=coords.map(c=>c[0]),lat=coords.map(c=>c[1]);
  const cx=(Math.min(...lon)+Math.max(...lon))/2, cy=(Math.min(...lat)+Math.max(...lat))/2;
  const proj=d3.geoConicEqualArea().parallels([cy-3,cy+3]).rotate([-cx,0]).fitExtent([[70,60],[W-70,H-60]],{type:'MultiPoint',coordinates:coords});
  proj.clipExtent([[-20,-20],[W+20,H+20]]);
  const path=d3.geoPath(proj);
  const base=R.country==='usa'?states:countries;
  const st=base.filter(s=>{const b=path.bounds(s);return b[1][0]>0&&b[0][0]<W&&b[1][1]>0&&b[0][1]<H;}).map(s=>`<path class="rm-state" d="${(path(s)||'').replace(/-?\d+\.\d+/g,m=>Math.round(+m))}"/>`).join('');
  const line='M'+coords.map(c=>proj(c).map(r).join(',')).join('L');
  // labels for overnights (dedupe), start marker
  const seen=new Set(); let dots='',labels='';
  const ov=[...new Set(R.overnights.concat([R.route[0],R.route[R.route.length-1]]))];
  const placed=[];for(const n of ov){const [x,y]=proj(all[n]).map(r); if(placed.some(([a,b])=>Math.hypot(a-x,b-y)<16)){dots+=`<circle class="rm-stop" cx="${x}" cy="${y}" r="6"/>`;continue;} placed.push([x,y]); dots+=`<circle class="rm-stop" cx="${x}" cy="${y}" r="6"/>`;
    const short=n.replace(/, [A-Z]{2}$/,''); const right=x<W*0.62;
    labels+=`<text class="rm-label" x="${right?x+11:x-11}" y="${y+5}" text-anchor="${right?'start':'end'}">${short}</text>`;}
  for(const n of (R.marks||[])){const [x,y]=proj(all[n]).map(r); const short=n.replace(/, [A-Z]{2}$/,''); const right=x<W*0.62;
    dots+=`<circle class="rm-mark" cx="${x}" cy="${y}" r="4.5"/>`; labels+=`<text class="rm-label rm-label-s" x="${right?x+10:x-10}" y="${y+4}" text-anchor="${right?'start':'end'}">${short}</text>`;}
  const svg=`<svg class="routemap" viewBox="0 0 ${W} ${H}" role="img" aria-label="Route map: ${R.overnights.join(', ')}"><defs><clipPath id="rmclip"><rect width="${W}" height="${H}" rx="10"/></clipPath></defs><g clip-path="url(#rmclip)"><rect class="rm-bg" width="${W}" height="${H}"/>${st}</g><path class="rm-route" d="${line}"/>${dots}${labels}</svg>`;
  fs.writeFileSync(f.replace('.json','.map.svg'),svg);
  console.log(f, svg.length);
}
