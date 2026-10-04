(function(){
  var groups=[].slice.call(document.querySelectorAll('.photos'));
  if(!groups.length)return;
  var box=document.createElement('div');box.className='lb';box.hidden=true;
  box.innerHTML='<button class="lb-x" aria-label="Close">&times;</button><button class="lb-p" aria-label="Previous photo">&#8249;</button><figure><img alt=""><figcaption></figcaption><p class="lb-n"></p></figure><button class="lb-nx" aria-label="Next photo">&#8250;</button>';
  document.body.appendChild(box);
  var img=box.querySelector('img'),cap=box.querySelector('figcaption'),num=box.querySelector('.lb-n'),items=[],i=0,sx=null;
  function show(){var f=items[i];img.src=f.querySelector('a').getAttribute('href');img.alt=f.querySelector('img').alt;cap.innerHTML=f.querySelector('figcaption').innerHTML;num.textContent=(i+1)+' / '+items.length;
    box.querySelector('.lb-p').style.visibility=items.length>1?'':'hidden';box.querySelector('.lb-nx').style.visibility=items.length>1?'':'hidden';}
  function open(g,k){items=[].slice.call(g.querySelectorAll('figure'));i=k;show();box.hidden=false;document.body.style.overflow='hidden';}
  function close(){box.hidden=true;img.src='';document.body.style.overflow='';}
  function go(d){i=(i+d+items.length)%items.length;show();}
  groups.forEach(function(g){[].slice.call(g.querySelectorAll('figure > a')).forEach(function(a,k){a.addEventListener('click',function(e){e.preventDefault();open(g,k);});});});
  box.querySelector('.lb-x').onclick=close;box.querySelector('.lb-p').onclick=function(){go(-1)};box.querySelector('.lb-nx').onclick=function(){go(1)};
  box.addEventListener('click',function(e){if(e.target===box)close();});
  document.addEventListener('keydown',function(e){if(box.hidden)return;if(e.key==='Escape')close();if(e.key==='ArrowLeft')go(-1);if(e.key==='ArrowRight')go(1);});
  box.addEventListener('touchstart',function(e){sx=e.touches[0].clientX;},{passive:true});
  box.addEventListener('touchend',function(e){if(sx===null)return;var dx=e.changedTouches[0].clientX-sx;if(Math.abs(dx)>40)go(dx<0?1:-1);sx=null;});
})();
