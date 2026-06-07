const { useState, useEffect } = React;
const { palette, coverBg, shotBg } = window;

function Detail({g, onBack, onOpen, fav, toggleFav}){
  const pal  = palette(g.id);
  const mono = (g.name||'??').slice(0,2).toUpperCase();

  const [igdb,     setIgdb]     = useState(null);
  const [loading,  setLoading]  = useState(true);
  const [lightbox, setLightbox] = useState(null);
  const [ytOpen,   setYtOpen]   = useState(false);

  useEffect(()=>{
    setIgdb(null); setLoading(true);
    fetch(`/api/igdb-ficha/?game_id=${g.id}`)
      .then(r=>r.ok ? r.json() : null)
      .then(d=>{ setIgdb(d); setLoading(false); })
      .catch(()=>setLoading(false));
  }, [g.id]);

  useEffect(()=>{
    if(!lightbox) return;
    const h=(e)=>{ if(e.key==='Escape') setLightbox(null); };
    window.addEventListener('keydown',h);
    return()=>window.removeEventListener('keydown',h);
  },[lightbox]);

  const coverSrc   = igdb?.cover_url  || g.image_url || null;
  const shots      = igdb?.screenshots || [];
  const chars      = igdb?.characters  || [];
  const similar    = igdb?.similar_games|| [];
  const videos     = igdb?.videos      || [];
  const altNames   = igdb?.alt_names   || [];
  const ageRatings = igdb?.age_ratings || [];
  const firstVideo = videos[0];

  const year  = igdb?.year  || g.year;
  const genre = igdb?.genre || g.genre;

  return (
    <>
      {lightbox && (
        <div className="lightbox" onClick={()=>setLightbox(null)}>
          <img src={lightbox} alt="screenshot" onClick={e=>e.stopPropagation()}/>
          <button className="lightbox-close" onClick={()=>setLightbox(null)}>✕ CERRAR</button>
        </div>
      )}

      <div className="subbar">
        <button className="backbtn" onClick={onBack}>‹ Biblioteca</button>
        <span className="crumb">{g.platform} / {genre}</span>
      </div>

      <div className="scroll screen-anim">
        <div className="detail">
          <div className="detail-grid">

            <div className="d-left">
              <div className="d-cover" style={{background: coverSrc ? undefined : coverBg(pal)}}>
                {coverSrc
                  ? <img src={coverSrc} alt={g.name}
                      style={{position:"absolute",inset:0,width:"100%",height:"100%",objectFit:"cover"}}/>
                  : <span className="mono">{mono}</span>}
              </div>
              <button className={"btn-play"+(fav?" on":"")} onClick={()=>toggleFav(g)}>
                {fav ? "★ EN MI LISTA" : "＋ GUARDAR"}
              </button>
            </div>

            <div>
              <h1 className="d-title">{igdb?.name || g.name}</h1>

              <div className="metarow">
                <span className="meta-chip"><b>{g.platform}</b></span>
                {year  && <span className="meta-chip">{year}</span>}
                {genre && <span className="meta-chip">{genre}</span>}
                {igdb?.game_modes?.map(m=>(
                  <span key={m} className="meta-chip">{m}</span>
                ))}
                {ageRatings.map((ar,i)=>(
                  <span key={i} className="age-chip">
                    <span className="org">{ar.org}</span>{ar.label}
                  </span>
                ))}
              </div>

              {(igdb?.critic_rating || igdb?.rating) && (
                <div className="ratings">
                  {igdb.critic_rating && (
                    <div className="rate">
                      <span className="num">{igdb.critic_rating}</span>
                      <span className="lab">Crítica
                        <b>{igdb.critic_rating_count ? `${igdb.critic_rating_count} reseñas` : ''}</b>
                      </span>
                    </div>
                  )}
                  {igdb.rating && (
                    <div className="rate">
                      <span className="num">{igdb.rating}</span>
                      <span className="lab">Usuarios
                        <b>{igdb.rating_count ? `${igdb.rating_count} reseñas` : ''}</b>
                      </span>
                    </div>
                  )}
                </div>
              )}

              {loading && <p className="d-summary" style={{color:"var(--muted-2)"}}>Cargando…</p>}
              {!loading && igdb?.summary && <p className="d-summary">{igdb.summary}</p>}

              {chars.length > 0 && (
                <>
                  <div className="sec-h">PERSONAJES</div>
                  <div className="chars">
                    {chars.map((c,i)=>(
                      <div className="char" key={i}>
                        <div className="mug">
                          {c.mug_url
                            ? <img src={c.mug_url} alt={c.name} loading="lazy"/>
                            : <span className="mono">{(c.name||'?').slice(0,2).toUpperCase()}</span>}
                        </div>
                        <div className="cn">{c.name}</div>
                      </div>
                    ))}
                  </div>
                </>
              )}

              {shots.length > 0 && (
                <>
                  <div className="sec-h">CAPTURAS</div>
                  <div className="gallery">
                    <div className="shot-main" onClick={()=>setLightbox(shots[0])}>
                      <img src={shots[0]} alt="screenshot 1" loading="lazy"/>
                    </div>
                    <div className="shot-strip">
                      {shots[1] && (
                        <div className="shot-sm" onClick={()=>setLightbox(shots[1])}>
                          <img src={shots[1]} alt="screenshot 2" loading="lazy"/>
                        </div>
                      )}
                      {shots.length > 2
                        ? <div className="shot-more" onClick={()=>setLightbox(shots[2])}>
                            {shots.length > 3 ? `+${shots.length-2} capturas` : shots[2] ? '▶ ver más' : ''}
                          </div>
                        : shots[2] && (
                          <div className="shot-sm" onClick={()=>setLightbox(shots[2])}>
                            <img src={shots[2]} alt="screenshot 3" loading="lazy"/>
                          </div>
                        )}
                    </div>
                  </div>
                </>
              )}

              {!loading && shots.length===0 && (
                <>
                  <div className="sec-h">CAPTURAS</div>
                  <div className="shots">
                    {[0,1,2].map(i=>(
                      <div className="shot" key={i} style={{background:shotBg(pal,i)}}>
                        <span style={{position:"absolute",left:8,bottom:6,
                          fontFamily:"var(--pixel-font)",fontSize:8,
                          color:"rgba(12,18,8,.6)"}}>{mono}·{i+1}</span>
                      </div>
                    ))}
                  </div>
                </>
              )}

              {firstVideo && (
                <>
                  <div className="sec-h">VIDEO</div>
                  {ytOpen
                    ? <iframe className="yt-embed" title={firstVideo.name}
                        src={`https://www.youtube.com/embed/${firstVideo.video_id}?autoplay=1`}
                        allow="autoplay; fullscreen" allowFullScreen/>
                    : <div className="trailer" onClick={()=>setYtOpen(true)}>
                        <span className="pl">▶</span>
                        <span className="tx">{firstVideo.name || 'Trailer oficial'}
                          <b>youtube.com · click para reproducir</b>
                        </span>
                      </div>}
                </>
              )}

              <div className="sec-h">FICHA TÉCNICA</div>
              <div className="specs">
                {(igdb?.developer||g.publisher) && (
                  <div className="spec"><span>Desarrolladora</span>
                    <b>{igdb?.developer||g.publisher}</b></div>
                )}
                {igdb?.publisher && (
                  <div className="spec"><span>Editora</span><b>{igdb.publisher}</b></div>
                )}
                {year && (
                  <div className="spec"><span>Lanzamiento</span><b>{year}</b></div>
                )}
                {igdb?.engines?.length > 0 && (
                  <div className="spec"><span>Motor</span><b>{igdb.engines.join(', ')}</b></div>
                )}
                {igdb?.franchises?.length > 0 && (
                  <div className="spec"><span>Saga</span><b>{igdb.franchises.join(', ')}</b></div>
                )}
                <div className="spec"><span>Ventas globales</span>
                  <b>{Number(g.global_sales||0).toFixed(2)} M</b>
                </div>
                {igdb?.platforms?.length > 0 && (
                  <div className="spec"><span>Plataformas</span>
                    <b>{igdb.platforms.slice(0,4).join(', ')}</b></div>
                )}
              </div>

              {altNames.length > 0 && (
                <>
                  <div className="sec-h">TAMBIÉN CONOCIDO COMO</div>
                  <div className="taglist">
                    {altNames.map((an,i)=>(
                      <span key={i} className="t" title={an.comment||''}>
                        {an.name}
                      </span>
                    ))}
                  </div>
                </>
              )}

              {similar.length > 0 && (
                <>
                  <div className="sec-h">JUEGOS SIMILARES</div>
                  <div className="sim">
                    {similar.map((sg,i)=>{
                      const sm = (sg.name||'??').slice(0,2).toUpperCase();
                      const clickable = sg.id && onOpen;
                      return (
                        <div className="tile" key={i}
                          onClick={clickable ? ()=>onOpen(sg) : undefined}
                          style={{cursor: clickable ? 'pointer' : 'default'}}>
                          <div className="art"
                            style={{background: sg.cover_url ? undefined : coverBg(palette(i))}}>
                            {sg.cover_url
                              ? <img src={sg.cover_url} alt={sg.name} loading="lazy"/>
                              : <span className="mono">{sm}</span>}
                          </div>
                          <div className="st">{sg.name}</div>
                        </div>
                      );
                    })}
                  </div>
                </>
              )}

              <div style={{height:40}}/>
            </div>
          </div>
        </div>

        <div className="mobile-playbar">
          <button className={"btn-play"+(fav?" on":"")} onClick={()=>toggleFav(g)}>
            {fav ? "★ EN MI LISTA" : "＋ GUARDAR"}
          </button>
        </div>
      </div>
    </>
  );
}

window.Detail = Detail;
