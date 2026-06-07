const { useState, useEffect } = React;

const PALETTES = [
  {sky:"#4a78c4",ground:"#2f5d34"},{sky:"#2a2150",ground:"#5a3a7a"},
  {sky:"#3a7a4a",ground:"#1d4a2a"},{sky:"#8a4a2a",ground:"#4a2a1a"},
  {sky:"#3a5a8a",ground:"#2a3a6a"},{sky:"#9a2a3a",ground:"#5a1a2a"},
  {sky:"#5aa0c4",ground:"#3a6a4a"},{sky:"#c46a2a",ground:"#6a3a1a"},
  {sky:"#2a2a4a",ground:"#7a2a5a"},{sky:"#2a6a8a",ground:"#1a4a5a"},
];

function palette(id){
  const n = typeof id === "number" ? id : parseInt(id, 10) || 0;
  return PALETTES[Math.abs(n) % PALETTES.length];
}

function coverBg(p){
  return `repeating-linear-gradient(0deg,rgba(0,0,0,.10) 0 3px,transparent 3px 6px),`
    +`repeating-linear-gradient(90deg,rgba(0,0,0,.07) 0 3px,transparent 3px 6px),`
    +`linear-gradient(180deg,${p.sky} 0%,${p.sky} 54%,${p.ground} 54%,${p.ground} 100%)`;
}

function shotBg(p,i){
  const split=[44,62,72][i%3];
  const a=i%2?p.ground:p.sky, b=i%2?p.sky:p.ground;
  return `repeating-linear-gradient(0deg,rgba(0,0,0,.12) 0 3px,transparent 3px 6px),`
    +`linear-gradient(180deg,${a} 0%,${a} ${split}%,${b} ${split}%,${b} 100%)`;
}

const PadIcon = (p) => (
  <svg viewBox="0 0 60 60" fill="none" {...p}>
    <rect x="32.5" y="35" width="5" height="5" rx="1" fill="currentColor"/>
    <rect x="17.5" y="27.5" width="5" height="15" rx="1" fill="currentColor"/>
    <rect x="27.5" y="32.5" width="5" height="15" rx="1" transform="rotate(90 27.5 32.5)" fill="currentColor"/>
    <rect x="40" y="30" width="5" height="5" rx="1" fill="currentColor"/>
    <path d="M35 20V18.12C35 16.62 35 15.87 34.58 15.33C34.15 14.79 33.43 14.61 31.97 14.24L28.03 13.26C26.57 12.89 25.85 12.71 25.42 12.17C25 11.63 25 10.88 25 9.38V5" stroke="currentColor" strokeWidth="4" strokeLinecap="round"/>
    <path d="M7.5 35C7.5 28.6 7.5 25.4 9.05 23.2C9.45 22.63 9.91 22.13 10.43 21.69C12.45 20 15.39 20 21.25 20H38.75C44.61 20 47.55 20 49.57 21.69C50.09 22.13 50.55 22.63 50.95 23.2C52.5 25.4 52.5 28.6 52.5 35C52.5 41.4 52.5 44.6 50.95 46.8C50.55 47.37 50.09 47.87 49.57 48.31C47.55 50 44.61 50 38.75 50H21.25C15.39 50 12.45 50 10.43 48.31C9.91 47.87 9.45 47.37 9.05 46.8C7.5 44.6 7.5 41.4 7.5 35Z" stroke="currentColor" strokeWidth="4"/>
  </svg>
);

const SearchIcon = () => (
  <svg viewBox="0 0 24 24" fill="none">
    <circle cx="10.5" cy="10.5" r="6.5" stroke="currentColor" strokeWidth="2.4"/>
    <path d="M20 20l-4.5-4.5" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round"/>
  </svg>
);

function useFitCount(ref, cardWidth=166){
  const [cols, setCols] = useState(6);
  useEffect(()=>{
    if(!ref.current) return;
    const ro = new ResizeObserver(([e])=>{
      setCols(Math.max(1, Math.floor(e.contentRect.width / cardWidth)));
    });
    ro.observe(ref.current);
    return ()=>ro.disconnect();
  }, [ref, cardWidth]);
  return cols;
}

Object.assign(window, { PALETTES, palette, coverBg, shotBg, PadIcon, SearchIcon, useFitCount });
