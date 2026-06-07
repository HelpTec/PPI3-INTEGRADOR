const { useState, useEffect, useRef } = React;
const { PadIcon, SearchIcon, Library, Catalog, EmuLibrary, Detail, RealEmulator, Emulator, Profile } = window;

function TopBar({query, setQuery, yearInput, setYearInput, screen, setScreen, onHome, onSearch, onProfile}){
  const auth = window.GB_AUTH;
  const submit = (e)=>{ e.preventDefault(); onSearch(query, yearInput); };
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
          placeholder="Buscar juego, plataforma o género…"/>
        <input
          type="number" min="1970" max="2029" value={yearInput}
          onChange={e=>setYearInput(e.target.value)}
          placeholder="Año"
          className="year-input"/>
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
  const [yearInput, setYearInput] = useState("");
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
    setQuery(""); setYearInput(""); setSearchResults(null); setSearchPage(1); setCatalog(null);
  };

  const doSearch = (q, plat, yr, page=1, append=false)=>{
    const hasFilter = q || (plat && plat!=="all") || yr;
    if(!hasFilter){ setSearchResults(null); return; }
    setIsSearching(true);
    searchQRef.current = q;
    const p = new URLSearchParams();
    if(q) p.set("q",q);
    if(plat && plat!=="all") p.set("platform",plat);
    if(yr){ p.set("year_from", yr); p.set("year_to", yr); }
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

  useEffect(()=>{
    if(query || yearInput) doSearch(query, filter, yearInput, 1, false);
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
          yearInput={yearInput} setYearInput={setYearInput}
          screen={screen} setScreen={setScreen}
          onHome={()=>{ home(); setScreen(s=>s==="emu-lib"?"emu-lib":"lib"); }}
          onSearch={(q,yr)=>doSearch(q,filter,yr,1,false)}
          onProfile={()=>setScreen("profile")}/>
      )}

      {screen==="lib" && (
        <Library
          shelves={shelves} platforms={platforms}
          filter={filter} setFilter={p=>{
            setFilter(p);
            if(p !== "all"){
              const shelf = shelves.find(s=>s.platform===p) || {platform:p, label:p};
              setCatalog(shelf);
              setScreen("catalogo");
            }
          }}
          onOpen={openGame} favs={favs} toggleFav={toggleFav}
          loading={loading}
          searchResults={searchResults} searchTotal={searchTotal}
          isSearching={isSearching}
          onLoadMore={()=>doSearch(query,filter,yearInput,searchPage+1,true)}
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
