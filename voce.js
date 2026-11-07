/* Voce cinese: sceglie la voce più naturale e adatta ai bambini tra quelle del dispositivo.
   Vale per tutte le lezioni: ogni frase in cinese passa da qui prima di essere letta. */
(function(){
  if(!(window.speechSynthesis) || window.__voceMaja) return;
  window.__voceMaja = true;
  var synth = window.speechSynthesis, scelta = null;

  // più in alto = preferita
  var ORDINE = [
    /xiaoyi/i,                         // Edge: voce di bambina (naturale)
    /yunxia/i,                         // Edge: voce di bambino (naturale)
    /xiaoxiao/i,                       // Edge: voce femminile naturale, molto dolce
    /xiaohan|xiaomeng|xiaomo|xiaoshuang|xiaoxuan|xiaoyou|xiaozhen|xiaorui|xiaoqiu|xiaochen/i,
    /yunxi|yunyang|yunjian|yunfeng|yunhao|yunye|yunze/i,
    /(natural|neural|online)/i,        // altre voci "naturali"
    /(premium|enhanced|增强|高级|優化|优化)/i, // voci Apple migliorate
    /google.*(普通话|mandarin|中国|chinese)/i, // Chrome
    /(lili|lilian|tingting|ting-ting|meijia|yu-shu|shasha|tian-tian|yaoyao|huihui|kangkang)/i
  ];
  function cinese(v){
    var l = (v.lang||'').replace('_','-').toLowerCase(), n = (v.name||'').toLowerCase();
    if(/^zh-hk|yue|cantonese|粤|粵/.test(l+' '+n)) return false;   // niente cantonese
    return /^zh|^cmn/.test(l);
  }
  function punteggio(v){
    var n = v.name||'', l = (v.lang||'').replace('_','-').toLowerCase();
    for(var i=0;i<ORDINE.length;i++) if(ORDINE[i].test(n)) return i*10 + (l==='zh-cn'?0:5);
    return 200 + (l==='zh-cn'?0:5) + (v.localService?0:-1);
  }
  function aggiorna(){
    var vv = (synth.getVoices()||[]).filter(cinese);
    vv.sort(function(a,b){ return punteggio(a)-punteggio(b) });
    scelta = vv[0] || null;
  }
  aggiorna();
  try{ synth.addEventListener('voiceschanged', aggiorna) }catch(e){ synth.onvoiceschanged = aggiorna }

  var parla = synth.speak.bind(synth);
  synth.speak = function(u){
    try{
      var testo = u.text||'', lang = (u.lang||'').toLowerCase();
      var eCinese = /^zh|^cmn/.test(lang) || (!lang && /[一-鿿]/.test(testo)) || (u.voice && cinese(u.voice));
      if(eCinese){
        if(!scelta) aggiorna();
        if(scelta){ u.voice = scelta; u.lang = scelta.lang }
        var n = scelta ? scelta.name : '';
        var bimbo = /xiaoyi|yunxia/i.test(n), naturale = /natural|neural|online|xiao|yun|premium|enhanced/i.test(n);
        // velocità: lenta ma non robotica
        u.rate = Math.min(Math.max(u.rate||1, naturale ? .82 : .78), .9);
        // tono: un po' più alto e allegro, tranne per le voci già di bambino
        u.pitch = bimbo ? 1 : (naturale ? 1.08 : 1.15);
      }
    }catch(e){}
    return parla(u);
  };
})();
