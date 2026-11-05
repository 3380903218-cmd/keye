/* Local photographs, bilingual descriptions and a native keyboard-accessible viewer. */
(() => {
  'use strict';
  const photographs=[...document.querySelectorAll('[data-cave-photograph]')];
  if(!photographs.length)return;
  let selected=null,returnFocus=null;
  const lang=()=>window.DUNHUANG_EXHIBITION.getState().lang;
  const dialog=document.createElement('dialog');dialog.id='cavePhotoDialog';dialog.className='cave-photo-dialog';dialog.setAttribute('aria-labelledby','cavePhotoTitle');dialog.setAttribute('aria-describedby','cavePhotoNote');
  dialog.innerHTML='<div class="photo-dialog-top"><h3 id="cavePhotoTitle"></h3><button class="photo-dialog-close" type="button" autofocus></button></div><img class="photo-dialog-image" alt=""/><p class="photo-dialog-note" id="cavePhotoNote"></p><div class="photo-dialog-credit photo-credit"></div>';
  document.body.append(dialog);
  function syncDialog(){
    if(!selected)return;
    const img=selected.querySelector('img');
    dialog.querySelector('h3').textContent=selected.querySelector('.photo-title').textContent;
    const full=dialog.querySelector('img');full.src=img.getAttribute('src');full.alt=img.alt;
    dialog.querySelector('.photo-dialog-note').textContent=selected.querySelector('.photo-note').textContent;
    dialog.querySelector('.photo-dialog-credit').innerHTML=selected.querySelector('.photo-credit').innerHTML;
  }
  function sync(){
    const zh=lang()==='zh';
    for(const figure of photographs){const section=figure.closest('.cave-photograph');section.setAttribute('aria-label',section.querySelector('h3').textContent);const img=figure.querySelector('img');img.alt=img.dataset[zh?'photoAltZh':'photoAltEn'];figure.querySelector('[data-photo-open]').setAttribute('aria-label',(zh?'查看照片：':'View photograph: ')+figure.querySelector('.photo-title').textContent);}
    dialog.querySelector('button').textContent=zh?'关闭 ×':'Close ×';syncDialog();
  }
  for(const figure of photographs){figure.querySelector('[data-photo-open]').addEventListener('click',e=>{selected=figure;returnFocus=e.currentTarget;syncDialog();dialog.showModal();document.body.classList.add('photo-viewer-open');});}
  dialog.querySelector('button').addEventListener('click',()=>dialog.close());
  dialog.addEventListener('click',e=>{if(e.target===dialog){const r=dialog.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)dialog.close();}});
  dialog.addEventListener('close',()=>{document.body.classList.remove('photo-viewer-open');returnFocus?.focus({preventScroll:true});});
  window.addEventListener('dunhuang:language',sync);sync();
})();
