(function(){
  var S=window.SITE, KEY="ms_cart_v1";
  var $=function(s,r){return (r||document).querySelector(s)};
  var money=function(n){return "$"+Number(n).toFixed(2)};
  var load=function(){try{return JSON.parse(localStorage.getItem(KEY))||[]}catch(e){return[]}};
  var save=function(c){try{localStorage.setItem(KEY,JSON.stringify(c))}catch(e){}; count();};
  function count(){var n=load().reduce(function(a,l){return a+l.qty},0);var el=$("#cart-count");if(el)el.textContent=n;}
  function sizes(){return S.product.sizes.filter(function(s){return s.enabled})}
  function flavors(){return S.product.flavors.filter(function(f){return f.enabled})}
  function size(id){return S.product.sizes.find(function(s){return s.id===id})}
  function flavor(id){return S.product.flavors.find(function(f){return f.id===id})}
  function boxes(c){return c.reduce(function(a,l){return a+l.qty},0)}
  function shipping(n){if(!n)return 0;var t=(S.shippingTiers||[]).find(function(t){return t.maxBoxes==null||n<=t.maxBoxes});return t?t.price:null}
  function esc(t){var d=document.createElement("div");d.textContent=t;return d.innerHTML}

  // nav
  var mb=$(".menu-btn");if(mb)mb.addEventListener("click",function(){var u=$("#menu");var o=u.classList.toggle("open");mb.setAttribute("aria-expanded",o)});
  count();

  // footer / contact links from config
  document.querySelectorAll("[data-email]").forEach(function(a){a.href="mailto:"+S.contactEmail;a.textContent=S.contactEmail});
  document.querySelectorAll("[data-instagram]").forEach(function(li){if(S.instagramUrl){li.hidden=false;li.querySelector("a").href=S.instagramUrl}else li.hidden=true});
  document.querySelectorAll("[data-price]").forEach(function(el){el.textContent=money(sizes()[0].price)});

  // ---- shop page
  var shop=$("#shop");
  if(shop){
    var sz=$("#sizes"),fl=$("#flavors"),price=$("#price");
    sz.innerHTML=sizes().map(function(s,i){return '<input type="radio" name="size" id="s-'+s.id+'" value="'+s.id+'"'+(i===0?' checked':'')+'><label for="s-'+s.id+'">'+esc(s.label)+'</label>'}).join("");
    fl.innerHTML=flavors().map(function(f,i){return '<input type="radio" name="flavor" id="f-'+f.id+'" value="'+f.id+'"'+(i===0?' checked':'')+'><label for="f-'+f.id+'">'+esc(f.name)+'</label>'}).join("");
    if(sizes().length<2)$("#size-field").hidden=true;
    var upd=function(){var s=size($('input[name=size]:checked').value);price.textContent=money(s.price)};
    sz.addEventListener("change",upd);upd();
    var q=$("#qty");
    $("#minus").onclick=function(){q.value=Math.max(1,+q.value-1)};
    $("#plus").onclick=function(){q.value=Math.min(20,+q.value+1)};
    // flavor photo + subtitle follow the selected flavor
    var flavorImg={
      classic:{src:"images/hero.jpg",alt:"Kraft box of nine classic Swiss meringues in sage-green cups"},
      coffee:{src:"images/coffee.jpg",alt:"Kraft box of nine coffee meringues tied with twine, beside coffee beans and an espresso",pos:"25% 50%"},
      chocolate:{src:"images/chocolate.jpg",alt:"Kraft box of nine chocolate meringues tied with twine, beside pieces of dark chocolate",pos:"25% 50%"}
    };
    var showFlavor=function(id){
      var f=flavor(id),line=$("#flavor-line");if(f&&line)line.textContent=f.name+" Swiss Meringue";
      var m=flavorImg[id];if(!m)return;var im=$("#main-img");im.src=m.src;im.alt=m.alt;im.style.objectPosition=m.pos||"";
      document.querySelectorAll(".thumbs button").forEach(function(x){x.setAttribute("aria-pressed",x.dataset.src===m.src)});
    };
    fl.addEventListener("change",function(){showFlavor($('input[name=flavor]:checked').value)});
    // preselect flavor from ?flavor=
    var p=new URLSearchParams(location.search).get("flavor");if(p&&$("#f-"+p)){$("#f-"+p).checked=true;showFlavor(p)}
    $("#add").onclick=function(){
      var c=load(),s=$('input[name=size]:checked').value,f=$('input[name=flavor]:checked').value,n=Math.max(1,Math.min(20,parseInt(q.value)||1));
      var ex=c.find(function(l){return l.size===s&&l.flavor===f});
      if(ex)ex.qty=Math.min(20,ex.qty+n);else c.push({size:s,flavor:f,qty:n});
      save(c);var m=$("#added");m.classList.add("show");m.focus&&m.focus();
    };
    document.querySelectorAll(".thumbs button").forEach(function(b){b.onclick=function(){
      $("#main-img").src=b.dataset.src;$("#main-img").alt=b.dataset.alt;$("#main-img").style.objectPosition="";
      document.querySelectorAll(".thumbs button").forEach(function(x){x.setAttribute("aria-pressed",x===b)})}});
  }

  // ---- cart page
  var cartEl=$("#cart");
  if(cartEl){
    var imgFor={classic:"images/classic.jpg",coffee:"images/coffee.jpg",chocolate:"images/chocolate.jpg"};
    var render=function(){
      var c=load(),box=$("#lines"),sum=$("#summary");
      if(!c.length){box.innerHTML='<div class="empty"><p class="lede">Your cart is empty.</p><div class="btn-row" style="justify-content:center"><a class="btn" href="/shop">Shop PETITES</a></div></div>';sum.hidden=true;return}
      sum.hidden=false;var sub=0;
      box.innerHTML=c.map(function(l,i){var s=size(l.size),f=flavor(l.flavor);if(!s||!f)return"";sub+=s.price*l.qty;
        return '<div class="line"><img src="'+(imgFor[l.flavor]||"images/closeup.jpg")+'" alt=""><div><h3>'+esc(S.product.name)+' — '+esc(f.name)+'</h3><div class="meta">'+esc(s.label)+' · '+money(s.price)+' each</div><button class="rm" data-i="'+i+'">Remove</button></div><div class="qty" aria-label="Quantity"><button data-d="-1" data-i="'+i+'" aria-label="Decrease">−</button><input value="'+l.qty+'" readonly aria-label="Quantity"><button data-d="1" data-i="'+i+'" aria-label="Increase">+</button></div></div>'}).join("");
      $("#sub").textContent=money(sub);
      var n=boxes(c),ship=shipping(n);
      $("#ship").textContent=ship==null?"Calculated at confirmation":ship===0?"Free":money(ship);
      $("#total").textContent=ship==null?money(sub)+" + shipping":money(sub+ship);
      var hint=$("#ship-hint"),T=S.shippingTiers||[],fi=T.findIndex(function(t){return t.price===0});
      if(hint){var left=fi>0?T[fi-1].maxBoxes+1-n:0;
        hint.textContent=ship===0?"Your order ships free.":left>0?"Add "+left+" more box"+(left>1?"es":"")+" for free shipping.":"";}
    };
    cartEl.addEventListener("click",function(e){
      var t=e.target,i=t.dataset.i;if(i==null)return;var c=load();
      if(t.classList.contains("rm"))c.splice(i,1);else if(t.dataset.d){c[i].qty=Math.max(1,Math.min(20,c[i].qty+ +t.dataset.d))}
      save(c);render();
    });
    var btn=$("#checkout");btn.textContent=S.checkoutLabel;
    btn.addEventListener("click",function(){
      var m=$("#soon");
      if(!S.checkoutEndpoint){m.classList.add("show");return}
      var label=btn.textContent;btn.disabled=true;btn.textContent="Redirecting to secure payment…";
      var fail=function(why){btn.disabled=false;btn.textContent=label;m.innerHTML='Sorry, we could not open the payment page. Please try again or <a href="/contact">contact us</a>.<br><small style="opacity:.7">'+esc(String(why||""))+'</small>';m.classList.add("show");if(window.console)console.error("Checkout failed:",why)};
      fetch(S.checkoutEndpoint,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({items:load()})})
        .then(function(r){return r.text().then(function(t){try{return JSON.parse(t)}catch(e){throw new Error("Unexpected reply from checkout ("+r.status+"): "+t.slice(0,80))}})})
        .then(function(d){if(d&&d.url)window.location.href=d.url;else fail(d&&d.error)}).catch(function(e){fail(e&&e.message)});
    });
    render();
  }

  // ---- thank-you page (Stripe success redirect): empty the cart
  if($("#thanks"))save([]);

  // ---- forms (contact + newsletter)
  document.querySelectorAll("form[data-form]").forEach(function(form){
    form.addEventListener("submit",function(e){
      e.preventDefault();
      var ok=form.parentElement.querySelector(".ok")||form.querySelector(".ok");
      var data=new FormData(form),kind=form.dataset.form;
      var done=function(){form.reset();if(ok)ok.classList.add("show")};
      if(S.formEndpoint){
        fetch(S.formEndpoint,{method:"POST",body:data,headers:{Accept:"application/json"}}).then(function(r){if(r.ok)done();else alert("Something went wrong. Please email "+S.contactEmail)}).catch(function(){alert("Something went wrong. Please email "+S.contactEmail)});
      }else{
        var subj=kind==="contact"?(data.get("subject")||"Message from the website"):"Newsletter sign-up";
        var body=kind==="contact"?"Name: "+data.get("name")+"\nEmail: "+data.get("email")+"\n\n"+data.get("message"):"Please add me to the Meringue Suisse list: "+data.get("email");
        window.location.href="mailto:"+S.contactEmail+"?subject="+encodeURIComponent(subj)+"&body="+encodeURIComponent(body);
        done();
      }
    });
  });
})();
