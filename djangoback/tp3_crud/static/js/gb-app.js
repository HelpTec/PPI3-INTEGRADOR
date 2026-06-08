const { useState, useEffect, useRef } = React;
const { PadIcon, SearchIcon, Library, Catalog, EmuLibrary, Detail, RealEmulator, Emulator, Profile } = window;

/* Extrae un año de 4 dígitos (1970-2029) del texto de búsqueda */
function parseQuery(raw) {
  const m = (raw || '').match(/\b(19[7-9]\d|20[0-2]\d)\b/);
  return {
    text: m ? raw.replace(m[0], '').replace(/\s+/, ' ').trim() : (raw || '').trim(),
    year: m ? parseInt(m[1]) : null,
  };
}

function TopBar({query, setQuery, screen, setScreen, onHome, onSearch, onProfile}){
  const auth = window.GB_AUTH;
  const submit = (e)=>{ e.preventDefault(); onSearch(query); };
  const onLib    = ()=>{ onHome(); setScreen("lib"); };
  const onEmuLib = ()=>{ onHome(); setScreen("emu-lib"); };

  return (
    <div className="topbar">
      <div className="tb-brand" onClick={onLib} title="Inicio">
        <PadIcon style={{width:30,height:30}}/>
        <span className="nm">GAME<b>BASE</b></span>
      </div>

      <div className="tb-nav">
        <button className={screen==="lib"||screen==="ficha"||screen==="catalogo"?"active":""}
          onClick={onLib}>BIBLIOTECA</button>
        <button className={screen==="emu-lib"?"active":""} onClick={onEmuLib}>EMULADOR</button>
      </div>

      <form className="search" onSubmit={submit}>
        <SearchIcon/>
        <input value={query} onChange={e=>setQuery(e.target.value)}
          placeholder="Buscar juego, plataforma, género o año…"/>
        <kbd>/</kbd>
      </form>

      <div className="tb-right">
        {auth.authenticated ? (
          <div className="tb-user">
            <button className="tb-user-btn" onClick={onProfile} title="Ver mi perfil">
              {auth.username}
            </button>
            <form action={auth.logoutUrl} method="post" style={{display:"inline"}}>
              <input type="hidden" name="csrfmiddlewaretoken" value={auth.csrfToken}/>
              <button type="submit" style={{background:"none",border:"none",cursor:"pointer",
                fontFamily:"var(--pixel-font)",fontSize:10,color:"var(--muted)"}}
                title="Cerrar sesión">✕</button>
            </form>
          </div>
        ) : (
          <a href={auth.loginUrl} className="tb-user"
            style={{textDecoration:"none",display:"block"}}>Iniciar sesión</a>
        )}
      </div>
    </div>
  );
}

function App(){
  const [screen,  setScreen]  = useState("lib");
  const [game,    setGame]    = useState(null);
  const [catalog, setCatalog] = useState(null);
  const [query,   setQuery]   = useState("");
  const [filter,  setFilter]  = useState("all");
  const [favs, setFavs] = useState(()=>{
    try{
      const raw = JSON.parse(localStorage.getItem("gb_favs")||"{}");
      const out={};
      for(const [k,v] of Object.entries(raw)){ if(v&&typeof v==="object") out[k]=v; }
      return out;
    }catch(e){return{};}
  });

  const [shelves,   setShelves]   = useState([]);
  const [platforms, setPlatforms] = useState([]);
  const [loading,   setLoading]   = useState(true);

  const [searchResults, setSearchResults] = useState(null);
  const [searchTotal,   setSearchTotal]   = useState(0);
  const [searchPage,    setSearchPage]    = useState(1);
  const [isSearching,   setIsSearching]   = useState(false);
  const searchQRef = useRef("");

  useEffect(()=>{
    try{localStorage.setItem("gb_favs",JSON.stringify(favs));}catch(e){}
  },[favs]);

  useEffect(()=>{
    fetch("/api/juegos/")
      .then(r=>r.json())
      .then(d=>{ setShelves(d.shelves||[]); setPlatforms(d.platforms||[]); setLoading(false); })
      .catch(()=>setLoading(false));
  },[]);

  const toggleFav = (g)=>setFavs(f=>{const n={...f};n[g.id]?delete n[g.id]:n[g.id]=g;return n;});
  const openGame  = (g)=>{ setGame(g); setScreen("ficha"); };
  const play      = (g)=>{ setGame(g); setScreen("emu"); };

  const home = ()=>{
    setQuery(""); setSearchResults(null); setSearchPage(1); setCatalog(null);
  };

  const doSearch = (q, plat, page=1, append=false)=>{
    const { text, year } = parseQuery(q);
    const hasFilter = text || (plat && plat!=="all") || year;
    if(!hasFilter){ setSearchResults(null); return; }
    setIsSearching(true);
    searchQRef.current = q;
    const p = new URLSearchParams();
    if(text) p.set("q", text);
    if(plat && plat!=="all") p.set("platform", plat);
    if(year){ p.set("year_from", year); p.set("year_to", year); }
    p.set("page", page);
    fetch("/api/juegos/?"+p)
      .then(r=>r.json())
      .then(d=>{
        if(searchQRef.current!==q) return;
        setSearchResults(prev=>append?(prev||[]).concat(d.games):d.games);
        setSearchTotal(d.total);
        setSearchPage(page);
        setIsSearching(false);
      })
      .catch(()=>setIsSearching(false));
  };

  /* Búsqueda en tiempo real con debounce 350ms */
  useEffect(()=>{
    if(!query){ setSearchResults(null); return; }
    const timer = setTimeout(()=>doSearch(query, filter, 1, false), 350);
    return ()=>clearTimeout(timer);
  },[query]);

  /* Si cambia el filtro de plataforma y hay búsqueda activa, refiltra */
  useEffect(()=>{
    if(query) doSearch(query, filter, 1, false);
    else setSearchResults(null);
  },[filter]);

  useEffect(()=>{
    const h=(e)=>{
      if(e.key==="/" && (screen==="lib"||screen==="catalogo")
         && document.activeElement.tagName!=="INPUT"){
        e.preventDefault();
        document.querySelector(".search input")?.focus();
      }
    };
    window.addEventListener("keydown",h);
    return()=>window.removeEventListener("keydown",h);
  },[screen]);

  const showTopBar = screen !== "emu";

  return (
    <div className="app">
      {showTopBar && (
        <TopBar query={query} setQuery={setQuery}
          screen={screen} setScreen={setScreen}
          onHome={()=>{ home(); setScreen(s=>s==="emu-lib"?"emu-lib":"lib"); }}
          onSearch={(q)=>doSearch(q,filter,1,false)}
          onProfile={()=>setScreen("profile")}/>
      )}

      {screen==="lib" && (
        <Library
          shelves={shelves} platforms={platforms}
          filter={filter} setFilter={p=>{
            setFilter(p);
            if(p !== "all" && !query){
              const shelf = shelves.find(s=>s.platform===p) || {platform:p, label:p};
              setCatalog(shelf);
              setScreen("catalogo");
            }
          }}
          onOpen={openGame} favs={favs} toggleFav={toggleFav}
          loading={loading}
          searchResults={searchResults} searchTotal={searchTotal}
          isSearching={isSearching}
          onLoadMore={()=>doSearch(query,filter,searchPage+1,true)}
          onSeeAll={shelf=>{ setCatalog(shelf); setScreen("catalogo"); }}
        />
      )}

      {screen==="catalogo" && catalog && (
        <Catalog shelf={catalog} onOpen={openGame} favs={favs} toggleFav={toggleFav}
          onBack={()=>{ setFilter("all"); setScreen("lib"); }}/>
      )}

      {screen==="emu-lib" && (
        <EmuLibrary onPlay={play}/>
      )}

      {screen==="ficha" && game && (
        <Detail g={game} onBack={()=>setScreen("lib")} onOpen={openGame}
          fav={!!favs[game.id]} toggleFav={toggleFav}/>
      )}

      {screen==="emu" && game && (
        game.core
          ? <RealEmulator key={game.id} g={game} onExit={()=>setScreen("emu-lib")}/>
          : <Emulator     key={game.id} g={game} onExit={()=>setScreen("emu-lib")}/>
      )}

      {screen==="profile" && (
        <Profile favs={favs} onOpen={openGame} toggleFav={toggleFav}
          onBack={()=>setScreen("lib")}/>
      )}
    </div>
  );
}

ReactDOM.createRoot(document.getElementById("gb-root")).render(<App/>);
