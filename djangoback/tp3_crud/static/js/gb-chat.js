(function(){
  var fab    = document.getElementById('chatFab');
  var panel  = document.getElementById('chatPanel');
  var body   = document.getElementById('chatBody');
  var form   = document.getElementById('chatForm');
  var input  = document.getElementById('chatInput');
  var seeded = false;
  var csrf   = window.GB_AUTH.csrfToken;

  function addMsg(text, who, id){
    var d = document.createElement('div');
    d.className = 'msg ' + who;
    d.textContent = text;
    if(id) d.id = id;
    body.appendChild(d);
    body.scrollTop = body.scrollHeight;
    return d;
  }

  function openChat(){
    panel.classList.add('open');
    panel.setAttribute('aria-hidden','false');
    fab.querySelector('.dot').style.display = 'none';
    if(!seeded){
      addMsg('¡Hola! Spawnée para ayudarte. Preguntame sobre cualquier juego, consola o época del catálogo.','bot');
      seeded = true;
    }
    setTimeout(function(){ input.focus(); }, 120);
  }

  function closeChat(){
    panel.classList.remove('open');
    panel.setAttribute('aria-hidden','true');
  }

  fab.addEventListener('click', function(){
    panel.classList.contains('open') ? closeChat() : openChat();
  });
  document.getElementById('chatClose').addEventListener('click', closeChat);

  form.addEventListener('submit', function(e){
    e.preventDefault();
    var msg = input.value.trim();
    if(!msg) return;
    addMsg(msg, 'me');
    input.value = '';

    var typingId = 'typing-' + Date.now();
    addMsg('escribiendo…', 'typing', typingId);

    fetch('/api/chat/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrf
      },
      body: JSON.stringify({ message: msg })
    })
    .then(function(r){ return r.json(); })
    .then(function(data){
      var t = document.getElementById(typingId);
      if(t) t.remove();
      addMsg(data.reply || 'Sin respuesta.', 'bot');
    })
    .catch(function(){
      var t = document.getElementById(typingId);
      if(t) t.remove();
      addMsg('Error de conexión con la IA.', 'bot');
    });
  });
})();
