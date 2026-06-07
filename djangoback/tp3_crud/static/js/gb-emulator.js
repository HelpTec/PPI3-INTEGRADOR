const { useState, useEffect, useRef, useCallback } = React;
const { PALETTES, coverBg } = window;

/*
  EMULABLES — fuente de verdad de los juegos con emulación.
  Para agregar un juego real:
    1. Copiá el archivo ROM a djangoback/tp3_crud/static/roms/
    2. Editá la entrada: rom: "/static/roms/archivo.ext"
  rom: null  → abre el juego demo interno
  core: clave de EmulatorJS ("nes"|"snes"|"gb"|"gbc"|"gba"|"segaMD"|"n64"|"psx")
*/
const EMULABLES = [
  {
    id: "emu-demo", name: "GameBase Demo", platform: "DEMO",
    image_url: "", pal_idx: 0,
    rom: null, core: null,
  },
  {
    id: "emu-nes", name: "Pentablocat", platform: "NES",
    image_url: "https://img.itch.zone/aW1nLzExMDM0ODk4LnBuZw==/original/XB0rbn.png", pal_idx: 2,
    rom: "/static/roms/pentablocat.nes", core: "nes",
  },
  {
    id: "emu-nes2", name: "BladeBuster", platform: "NES",
    image_url: "https://www.retrones.net/sites/default/files/capturas/BladeBuster%20201409210915237.png", pal_idx: 5,
    rom: "/static/roms/BladeBuster.nes", core: "nes",
  },
  {
    id: "emu-nes3", name: "DesertEscape", platform: "NES",
    image_url: "https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/f/ba7bee9d-0965-409c-a653-9490f8941cd7/dhnjw47-c6248122-e67e-4f6b-a4fd-369e852754bb.png/v1/fit/w_828,h_1160/desert_escape__by_hjrodrigo_dhnjw47-414w-2x.png?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1cm46YXBwOjdlMGQxODg5ODIyNjQzNzNhNWYwZDQxNWVhMGQyNmUwIiwiaXNzIjoidXJuOmFwcDo3ZTBkMTg4OTgyMjY0MzczYTVmMGQ0MTVlYTBkMjZlMCIsIm9iaiI6W1t7ImhlaWdodCI6Ijw9MTc5MyIsInBhdGgiOiIvZi9iYTdiZWU5ZC0wOTY1LTQwOWMtYTY1My05NDkwZjg5NDFjZDcvZGhuanc0Ny1jNjI0ODEyMi1lNjdlLTRmNmItYTRmZC0zNjllODUyNzU0YmIucG5nIiwid2lkdGgiOiI8PTEyODAifV1dLCJhdWQiOlsidXJuOnNlcnZpY2U6aW1hZ2Uub3BlcmF0aW9ucyJdfQ.UcdHcZU_gbhlJD0OikK7rKGzm3gUuL4vYj-j7ZPQ2ec", pal_idx: 8,
    rom: "/static/roms/Desert Escape! v1.1.nes", core: "nes",
  },
];

function useRomStatus(rom){
  const [status, setStatus] = useState(rom ? "checking" : "demo");
  useEffect(()=>{
    if(!rom){ setStatus("demo"); return; }
    fetch(rom, {method:"HEAD"})
      .then(r=>setStatus(r.ok ? "ready" : "missing"))
      .catch(()=>setStatus("missing"));
  },[rom]);
  return status;
}

function EmuCard({g, onPlay}){
  const pal    = PALETTES[g.pal_idx];
  const status = useRomStatus(g.rom);

  const badge = {
    demo:     {label:"▶ JUGAR",   color:"var(--green)"},
    ready:    {label:"▶ JUGAR",   color:"var(--green)"},
    checking: {label:"…",         color:"var(--green-d)"},
    missing:  {label:"ROM FALTA", color:"#d8623c"},
  }[status];

  return (
    <button className="emu-card"
      onClick={()=> status !== "missing" && onPlay(g)}
      style={{opacity: status==="missing" ? .55 : 1,
              cursor:  status==="missing" ? "default" : "pointer"}}>
      <div className="emu-cover"
        style={{background: g.image_url ? undefined : coverBg(pal)}}>
        {g.image_url && <img src={g.image_url} alt={g.name}/>}
        <div className="emu-badge">
          <span style={{background: badge.color, fontSize: badge.label.length>2?"11px":"20px"}}>
            {badge.label}
          </span>
        </div>
        {g.core === null && (
          <span style={{position:"absolute",top:6,left:6,
            fontFamily:"var(--pixel-font)",fontSize:8,
            background:"var(--green-d)",color:"var(--green-2)",
            padding:"2px 6px",zIndex:3}}>DEMO</span>
        )}
      </div>
      <div className="emu-info">
        <div className="emu-title">{g.name}</div>
        <div className="emu-con">{g.platform}</div>
        {status==="missing" && (
          <div style={{fontFamily:"var(--pixel-font)",fontSize:8,
            color:"#d8623c",marginTop:4}}>
            Agregá {g.rom?.split("/").pop()}
          </div>
        )}
      </div>
    </button>
  );
}

function EmuLibrary({onPlay}){
  return (
    <div className="emu-library screen-anim">
      <h2>EMULADOR</h2>
      <p>Seleccioná un juego para empezar a jugar.</p>
      <div className="emu-cards">
        {EMULABLES.map(g=>(
          <EmuCard key={g.id} g={g} onPlay={onPlay}/>
        ))}
      </div>
    </div>
  );
}

function RealEmulator({g, onExit}){
  const [romOk, setRomOk] = useState(null);

  useEffect(()=>{
    fetch(g.rom, {method:"HEAD"})
      .then(r=>setRomOk(r.ok))
      .catch(()=>setRomOk(false));
  },[g.rom]);

  useEffect(()=>{
    if(romOk !== true) return;

    window.EJS_player         = "#ejs-container";
    window.EJS_core           = g.core;
    window.EJS_gameUrl        = g.rom;
    window.EJS_pathtodata     = "https://cdn.emulatorjs.org/stable/data/";
    window.EJS_startOnLoaded  = true;
    window.EJS_color          = "#9bbc0f";
    window.EJS_backgroundColor= "#0c0f0b";
    window.EJS_defaultOptions = {
      "save-state-slot": 1,
      "save-state-location": "keep in browser",
    };

    const script = document.createElement("script");
    script.src = "https://cdn.emulatorjs.org/stable/data/loader.js";
    script.id  = "ejs-loader";
    document.body.appendChild(script);

    return ()=>{
      try{
        if(window.EJS_emulator){
          if(window.EJS_emulator.pause) window.EJS_emulator.pause();
          if(window.EJS_emulator.module){
            var mod = window.EJS_emulator.module;
            if(mod._emscripten_cancel_main_loop) mod._emscripten_cancel_main_loop();
            var ac = (mod.SDL2 && mod.SDL2.audioContext) || window.EJS_emulator.audioContext;
            if(ac && ac.state !== "closed") ac.close();
          }
        }
      }catch(e){}
      var cont = document.getElementById("ejs-container");
      if(cont) cont.innerHTML = "";
      var ejsScripts = document.querySelectorAll('script[src*="emulatorjs"]');
      for(var i=0;i<ejsScripts.length;i++){ ejsScripts[i].remove(); }
      var ejsKeys = ["EJS_emulator","EJS_player","EJS_core","EJS_gameUrl","EJS_pathtodata",
        "EJS_startOnLoaded","EJS_color","EJS_backgroundColor","EJS_defaultOptions"];
      for(var j=0;j<ejsKeys.length;j++){ delete window[ejsKeys[j]]; }
    };
  },[romOk, g.rom, g.core]);

  useEffect(()=>{
    const h=(e)=>{ if(e.key==="Escape") onExit(); };
    window.addEventListener("keydown",h);
    return()=>window.removeEventListener("keydown",h);
  },[onExit]);

  return (
    <div className="emu-wrap">
      <div className="emu-top">
        <button className="backbtn" onClick={onExit}>‹ Salir</button>
        <span className="now">Jugando <b>{g.name}</b> · {g.platform}</span>
        <span className="live"><i></i>EN VIVO</span>
      </div>

      {romOk === null && (
        <div className="loading">CARGANDO ROM…</div>
      )}

      {romOk === false && (
        <div style={{flex:1,display:"grid",placeItems:"center",padding:40,textAlign:"center"}}>
          <div>
            <div style={{fontFamily:"var(--pixel-font)",fontSize:14,
              color:"#d8623c",marginBottom:20}}>ROM NO ENCONTRADA</div>
            <p style={{color:"var(--muted)",fontSize:20,maxWidth:"40ch",
              margin:"0 auto 28px",lineHeight:1.4}}>
              Copiá{" "}
              <span style={{color:"var(--green)",fontFamily:"var(--ui-font)"}}>
                {g.rom.split("/").pop()}
              </span>{" "}
              a <span style={{color:"var(--green)"}}>static/roms/</span> y recargá.
            </p>
            <button className="backbtn" onClick={onExit}>‹ Volver</button>
          </div>
        </div>
      )}

      {romOk === true && (
        <div style={{flex:1,minHeight:0,position:"relative",background:"#0c0f0b",overflow:"hidden"}}>
          <div id="ejs-container" style={{
            position:"absolute",inset:0,width:"100%",height:"100%"
          }}/>
        </div>
      )}
    </div>
  );
}

function fmt(s){const m=Math.floor(s/60),x=s%60;return(m<10?"0":"")+m+":"+(x<10?"0":"")+x;}
function spawnCoin(){return{id:Math.random(),x:10+Math.random()*78,y:14+Math.random()*64};}

function Emulator({g, onExit}){
  const pal = PALETTES[g.pal_idx ?? 0];
  const [pos,setPos]    = useState({x:50,y:55});
  const [coins,setCoins]= useState(()=>[spawnCoin(),spawnCoin(),spawnCoin()]);
  const [score,setScore]= useState(0);
  const [time,setTime]  = useState(0);
  const [saves,setSaves]= useState([]);
  const [pressed,setPressed] = useState(new Set());
  const [flash,setFlash]= useState("");
  const [aPulse,setAPulse]=useState(false);
  const held=useRef(new Set());
  const consoleRef=useRef(null);

  const hold=useCallback((n,on)=>{
    if(on)held.current.add(n);else held.current.delete(n);
    setPressed(p=>{const s=new Set(p);on?s.add(n):s.delete(n);return s;});
  },[]);
  const doA=useCallback(()=>{setAPulse(true);setTimeout(()=>setAPulse(false),180);},[]);

  useEffect(()=>{
    let raf,last=performance.now();
    const loop=(t)=>{
      const dt=Math.min(50,t-last)/16.7;last=t;
      setPos(p=>{
        let{x,y}=p;const s=1.5*dt;
        if(held.current.has("left"))x-=s; if(held.current.has("right"))x+=s;
        if(held.current.has("up"))y-=s;   if(held.current.has("down"))y+=s;
        return{x:Math.max(4,Math.min(92,x)),y:Math.max(8,Math.min(80,y))};
      });
      raf=requestAnimationFrame(loop);
    };
    raf=requestAnimationFrame(loop);
    return()=>cancelAnimationFrame(raf);
  },[]);

  useEffect(()=>{
    setCoins(cs=>{
      let hit=0;
      const left=cs.filter(c=>{
        const d=Math.hypot(c.x-pos.x,c.y-pos.y);
        if(d<7){hit++;return false;}return true;
      });
      if(hit){setScore(s=>s+hit*10);return left.concat(Array.from({length:hit},spawnCoin));}
      return cs;
    });
  },[pos]);

  useEffect(()=>{const id=setInterval(()=>setTime(t=>t+1),1000);return()=>clearInterval(id);},[]);

  useEffect(()=>{
    const map={ArrowLeft:"left",ArrowRight:"right",ArrowUp:"up",ArrowDown:"down",
               a:"left",d:"right",w:"up",s:"down"};
    const dn=(e)=>{
      const k=e.key.length===1?e.key.toLowerCase():e.key;
      if(map[k]){e.preventDefault();hold(map[k],true);}
      else if(k==="x"){hold("A",true);doA();}
      else if(k==="z"){hold("B",true);}
      else if(k==="Escape")onExit();
    };
    const up=(e)=>{
      const k=e.key.length===1?e.key.toLowerCase():e.key;
      if(map[k])hold(map[k],false);
      else if(k==="x")hold("A",false);
      else if(k==="z")hold("B",false);
    };
    window.addEventListener("keydown",dn);window.addEventListener("keyup",up);
    return()=>{window.removeEventListener("keydown",dn);window.removeEventListener("keyup",up);};
  },[hold,doA,onExit]);

  const save=()=>{
    setSaves(s=>[{id:Date.now(),t:fmt(time),score,x:pos.x,y:pos.y},...s].slice(0,6));
    setFlash("save"); setTimeout(()=>setFlash(""),520);
  };
  const loadSave=(s)=>{setPos({x:s.x,y:s.y});setScore(s.score);};
  const fullscreen=()=>{const el=consoleRef.current;if(el?.requestFullscreen)el.requestFullscreen();};
  const P=(n)=>pressed.has(n)?" press":"";

  return (
    <div className="emu-wrap">
      <div className="emu-top">
        <button className="backbtn" onClick={onExit}>‹ Salir</button>
        <span className="now">Jugando <b>{g.name}</b> · {g.platform}</span>
        <span className="live"><i></i>EN VIVO</span>
        <span style={{marginLeft:"auto",fontSize:17,color:"var(--muted)"}}>★ {score} · {fmt(time)}</span>
      </div>

      <div className="emu-stage">
        <div className="console" ref={consoleRef}>
          <div className="scr-frame">
            <div className="gbscreen" style={{backgroundColor:pal.ground}}>
              <span className="hud">{g.name.slice(0,2).toUpperCase()} ×{score/10}</span>
              <span className="hud2">{fmt(time)}</span>
              {coins.map(c=><span key={c.id} className="coin" style={{left:c.x+"%",top:c.y+"%"}}/>)}
              <div className="sprite" style={{left:pos.x+"%",top:pos.y+"%",
                transform:aPulse?"scale(1.35)":"scale(1)"}}/>
              <div className="ground"/>
            </div>
          </div>
          <div className="brand-plate">
            <span className="gb">GAME<b>BASE</b></span>
            <span className="pwr"><i></i>POWER</span>
          </div>
          <div className="controls">
            <div className="dpad">
              <button className="blank"/>
              <button className={P("up")}
                onPointerDown={()=>hold("up",true)} onPointerUp={()=>hold("up",false)}
                onPointerLeave={()=>hold("up",false)}>▲</button>
              <button className="blank"/>
              <button className={P("left")}
                onPointerDown={()=>hold("left",true)} onPointerUp={()=>hold("left",false)}
                onPointerLeave={()=>hold("left",false)}>◀</button>
              <button className="ctr"/>
              <button className={P("right")}
                onPointerDown={()=>hold("right",true)} onPointerUp={()=>hold("right",false)}
                onPointerLeave={()=>hold("right",false)}>▶</button>
              <button className="blank"/>
              <button className={P("down")}
                onPointerDown={()=>hold("down",true)} onPointerUp={()=>hold("down",false)}
                onPointerLeave={()=>hold("down",false)}>▼</button>
              <button className="blank"/>
            </div>
            <div className="startsel">
              <button className="pill">SELECT</button>
              <button className="pill">START</button>
            </div>
            <div className="ab">
              <button className={P("B")}
                onPointerDown={()=>hold("B",true)} onPointerUp={()=>hold("B",false)}
                onPointerLeave={()=>hold("B",false)}>B</button>
              <button className={aPulse?"press":""}
                onPointerDown={()=>{hold("A",true);doA();}} onPointerUp={()=>hold("A",false)}
                onPointerLeave={()=>hold("A",false)}>A</button>
            </div>
          </div>
        </div>
      </div>

      <div className="toolbar">
        <button className={"tool"+(flash==="save"?" flash":"")} onClick={save}>▤ Guardar estado</button>
        <button className="tool" onClick={()=>saves[0]&&loadSave(saves[0])}>▣ Cargar último</button>
        <button className="tool" onClick={fullscreen}>⛶ Pantalla completa</button>
        <button className="tool" onClick={onExit}>✕ Cerrar juego</button>
      </div>

      <div className="tray">
        <h4>ESTADOS GUARDADOS</h4>
        <div className="tray-grid">
          {saves.length===0 && (
            <div className="ss-empty">Aún no hay estados. Pulsa "Guardar estado" para crear uno.</div>
          )}
          {saves.map(s=>(
            <button className="ss" key={s.id} onClick={()=>loadSave(s)}
              style={{cursor:"pointer",textAlign:"left",padding:0}}>
              <div className="th" style={{backgroundColor:pal.ground}}>
                <span className="coin" style={{left:"40%",top:"40%",animation:"none"}}/>
              </div>
              <div className="cap"><span>{s.t}</span><b>★{s.score}</b></div>
            </button>
          ))}
        </div>
      </div>
      <div className="kbd-hint">
        Controles: <kbd>← ↑ → ↓</kbd> o <kbd>WASD</kbd> mover · <kbd>X</kbd> botón A ·
        <kbd>Z</kbd> botón B · recogé las monedas · <kbd>Esc</kbd> salir
      </div>
    </div>
  );
}

Object.assign(window, { EMULABLES, EmuLibrary, RealEmulator, Emulator });
