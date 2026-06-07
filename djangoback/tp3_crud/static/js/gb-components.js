const { useState, useEffect, useRef, useCallback } = React;
const { palette, coverBg, useFitCount } = window;

function Card({g, onOpen, fav, toggleFav}){
  const pal = palette(g.id);
  const mono = (g.name||'??').slice(0,2).toUpperCase();
  return (
    <button className="card" onClick={()=>onOpen(g)}>
      <div className="cover" style={{background: g.image_url ? undefined : coverBg(pal)}}>
        {g.image_url && <img src={g.image_url} alt={g.name} loading="lazy"/>}
        <span className="con-tag">{g.platform}</span>
        <span className={"fav"+(fav?" on":"")}
          onClick={e=>{e.stopPropagation(); toggleFav(g);}}>{fav?"★":"☆"}</span>
        {!g.image_url && <span className="mono">{mono}</span>}
      </div>
      <div className="c-title">{g.name}</div>
      <div className="c-meta">{g.year} · {g.genre}</div>
    </button>
  );
}

function ChipBar({filter, setFilter, platforms}){
  const top = ['NES','SNES','GB','GBA','GEN','N64','PS','PS2','DS'];
  const shown = top.filter(p=>platforms.includes(p));
  return (
    <div className="chipbar">
      <button className={"chip"+(filter==="all"?" on":"")} onClick={()=>setFilter("all")}>Todas</button>
      {shown.map(p=>(
        <button key={p} className={"chip"+(filter===p?" on":"")} onClick={()=>setFilter(p)}>{p}</button>
      ))}
    </div>
  );
}

function Shelf({shelf, onOpen, favs, toggleFav, onSeeAll}){
  const ref = useRef(null);
  const cols = useFitCount(ref);
  const visible = shelf.games.slice(0, cols);
  const total = shelf.total || shelf.games.length;

  return (
    <div className="shelf">
      <div className="shelf-head">
        <h3>{shelf.label} <span className="badge">{total}</span></h3>
        {total > visible.length && (
          <a href="#" onClick={e=>{e.preventDefault(); onSeeAll(shelf);}}>
            ver todo ({total}) ›
          </a>
        )}
      </div>
      <div ref={ref} className="shelf-grid">
        {visible.map(g=>(
          <Card key={g.id} g={g} onOpen={onOpen} fav={!!favs[g.id]} toggleFav={toggleFav}/>
        ))}
      </div>
    </div>
  );
}

function Catalog({shelf, onOpen, onBack, favs, toggleFav}){
  const [games,   setGames]   = useState([]);
  const [page,    setPage]    = useState(0);
  const [total,   setTotal]   = useState(0);
  const [loading, setLoading] = useState(false);

  const fetchPage = useCallback((p) => {
    setLoading(true);
    fetch("/api/juegos/?platform=" + encodeURIComponent(shelf.platform) + "&page=" + p)
      .then(r => r.json())
      .then(d => {
        setGames(prev => p === 1 ? (d.games || []) : prev.concat(d.games || []));
        setTotal(d.total || 0);
        setPage(p);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [shelf.platform]);

  useEffect(() => { fetchPage(1); }, [fetchPage]);

  return (
    <>
      <div className="subbar">
        <button className="backbtn" onClick={onBack}>‹ Biblioteca</button>
        <span className="crumb">{shelf.label}</span>
      </div>
      <div className="scroll screen-anim">
        {loading && games.length === 0 && <div className="loading">CARGANDO</div>}
        <div className="catalog-grid">
          {games.map(g=>(
            <Card key={g.id} g={g} onOpen={onOpen} fav={!!favs[g.id]} toggleFav={toggleFav}/>
          ))}
        </div>
        {games.length < total && (
          <div style={{textAlign:"center",padding:"0 22px 30px"}}>
            <button className="chip" onClick={()=>fetchPage(page+1)} disabled={loading}>
              {loading ? "Cargando…" : "Cargar más (" + (total - games.length) + " restantes)"}
            </button>
          </div>
        )}
        <div style={{height:30}}/>
      </div>
    </>
  );
}

function Library({shelves, platforms, filter, setFilter, onOpen, favs, toggleFav,
                  loading, searchResults, searchTotal, onLoadMore, isSearching, onSeeAll}){
  if(loading) return <div className="loading">CARGANDO</div>;

  if(searchResults !== null){
    return (
      <div className="scroll screen-anim">
        <ChipBar filter={filter} setFilter={setFilter} platforms={platforms}/>
        <div className="shelf">
          <div className="shelf-head">
            <h3>Resultados <span className="badge">{searchTotal}</span></h3>
          </div>
          <div className="catalog-grid">
            {searchResults.map(g=>(
              <Card key={g.id} g={g} onOpen={onOpen} fav={!!favs[g.id]} toggleFav={toggleFav}/>
            ))}
            {searchResults.length===0 && (
              <p style={{color:"var(--muted)",fontSize:20,gridColumn:"1/-1"}}>Sin resultados.</p>
            )}
          </div>
          {searchResults.length < searchTotal && (
            <div style={{textAlign:"center",padding:"0 22px 30px"}}>
              <button className="chip" onClick={onLoadMore} disabled={isSearching}>
                {isSearching ? "Cargando…" : "Cargar más"}
              </button>
            </div>
          )}
        </div>
      </div>
    );
  }

  const visibleShelves = filter==="all" ? shelves : shelves.filter(s=>s.platform===filter);
  return (
    <div className="scroll screen-anim">
      <ChipBar filter={filter} setFilter={setFilter} platforms={platforms}/>
      {visibleShelves.map(shelf=>(
        <Shelf key={shelf.platform} shelf={shelf}
          onOpen={onOpen} favs={favs} toggleFav={toggleFav}
          onSeeAll={onSeeAll}/>
      ))}
      <div style={{height:30}}/>
    </div>
  );
}

function Profile({favs, onOpen, toggleFav, onBack}){
  const auth = window.GB_AUTH;
  const games = Object.values(favs).filter(v=>v&&typeof v==="object");
  const initial = (auth.username||"?")[0].toUpperCase();
  return (
    <div className="profile-page">
      <button className="btn-back-profile" onClick={onBack}>
        <span>◀</span> VOLVER
      </button>
      <div className="profile-header">
        <div className="profile-avatar">{initial}</div>
        <div>
          <div className="profile-username">{auth.username}</div>
          <div className="profile-fav-count">{games.length} JUEGO{games.length!==1?"S":""} GUARDADO{games.length!==1?"S":""}</div>
        </div>
      </div>
      <div className="profile-section-title">MIS FAVORITOS</div>
      {games.length===0
        ? <div className="profile-empty">No tenés juegos guardados todavía.<br/>Presioná ★ en cualquier juego para agregarlo.</div>
        : <div className="profile-grid">
            {games.map(g=>(
              <Card key={g.id} g={g} onOpen={onOpen} fav={true} toggleFav={toggleFav}/>
            ))}
          </div>
      }
    </div>
  );
}

Object.assign(window, { Card, ChipBar, Shelf, Catalog, Library, Profile });
