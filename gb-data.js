/* GameBase · sample catalog (fictional titles to avoid real-game copyright) */
window.GB_CONSOLES = ["NES","SNES","Genesis","Game Boy","PS1","Arcade"];

window.GB_GAMES = [
  { id:"pk",  title:"Pixel Knight",        con:"NES",      year:1987, genre:"Plataformas", players:"1-2", dev:"Octogon Soft",   pub:"Famizo",       region:"NTSC", mono:"PK", sky:"#4a78c4", ground:"#2f5d34",
    desc:"Un caballero de 8 bits cruza ocho reinos para recuperar la Corona Astillada. Salta, esquiva y resuelve mazmorras llenas de trampas en este clásico de plataformas." },
  { id:"gr",  title:"Galaxy Raiders",      con:"NES",      year:1985, genre:"Shoot'em up", players:"1-2", dev:"Nova Lab",       pub:"Famizo",       region:"NTSC", mono:"GR", sky:"#2a2150", ground:"#5a3a7a",
    desc:"Defiende la última estación orbital de oleadas infinitas de invasores. Mejora tu nave entre niveles y enfréntate a jefes del tamaño de la pantalla." },
  { id:"sc",  title:"Slime Saga",          con:"NES",      year:1990, genre:"RPG",         players:"1",   dev:"Aurora Works",   pub:"Famizo",       region:"NTSC", mono:"SS", sky:"#3a7a4a", ground:"#1d4a2a",
    desc:"Recluta babosas de colores, súbelas de nivel y libra batallas por turnos en un mundo abierto pixelado lleno de secretos." },
  { id:"mt",  title:"Mega Tank Zero",      con:"NES",      year:1988, genre:"Acción",      players:"1-2", dev:"Bolt Dynamics",  pub:"Kaisei",       region:"NTSC", mono:"MT", sky:"#8a4a2a", ground:"#4a2a1a",
    desc:"Pilota un tanque modular por zonas de guerra destructibles. Combina piezas para crear el vehículo perfecto contra cada jefe." },

  { id:"cc",  title:"Crystal Caverns",     con:"SNES",     year:1992, genre:"Aventura",    players:"1",   dev:"Lumen Studio",   pub:"Sierra Pix",   region:"NTSC", mono:"CC", sky:"#3a5a8a", ground:"#2a3a6a",
    desc:"Explora cavernas generadas con efectos Modo-7, ilumina grutas con cristales y revela un mapa que cambia con la luz." },
  { id:"db",  title:"Bit Brawlers",        con:"SNES",     year:1994, genre:"Lucha",       players:"1-2", dev:"Knuckle Co.",    pub:"Sierra Pix",   region:"NTSC", mono:"BB", sky:"#9a2a3a", ground:"#5a1a2a",
    desc:"Doce luchadores pixelados, combos de seis botones y escenarios interactivos. El torneo definitivo de los 16 bits." },
  { id:"sk",  title:"Sky Kingdom",         con:"SNES",     year:1996, genre:"RPG",         players:"1",   dev:"Aurora Works",   pub:"Sierra Pix",   region:"NTSC", mono:"SK", sky:"#5aa0c4", ground:"#3a6a4a",
    desc:"Una épica por turnos a través de islas flotantes. Sistema de afinidad elemental y más de 40 horas de aventura." },
  { id:"tr",  title:"Turbo Racer 9",       con:"SNES",     year:1991, genre:"Carreras",    players:"1-2", dev:"Velocity X",     pub:"Sierra Pix",   region:"NTSC", mono:"T9", sky:"#c46a2a", ground:"#6a3a1a",
    desc:"Carreras a toda velocidad con pseudo-3D y pantalla dividida. Nueve circuitos, ocho coches y un modo campeonato." },

  { id:"nn",  title:"Neon Ninja",          con:"Genesis",  year:1992, genre:"Acción",      players:"1",   dev:"Blade Byte",     pub:"Megadrive Hz",region:"NTSC", mono:"NN", sky:"#2a2a4a", ground:"#7a2a5a",
    desc:"Un ninja cibernético recorre una ciudad de neón. Wall-jumps, sombras y un sistema de combos fluido a 60 fps." },
  { id:"vr",  title:"Volt Runner",         con:"Genesis",  year:1993, genre:"Plataformas", players:"1",   dev:"Velocity X",     pub:"Megadrive Hz",region:"NTSC", mono:"VR", sky:"#2a6a8a", ground:"#1a4a5a",
    desc:"Corre a la velocidad del rayo por bucles y rampas. Mantén el impulso para desbloquear rutas alternativas." },
  { id:"ab",  title:"Aqua Blaster",        con:"Genesis",  year:1991, genre:"Shoot'em up", players:"1-2", dev:"Nova Lab",       pub:"Megadrive Hz",region:"NTSC", mono:"AB", sky:"#2a7a8a", ground:"#1a4a6a",
    desc:"Disparos submarinos con scroll horizontal. Esquiva corrientes, recolecta torpedos y derrota al Kraken mecánico." },

  { id:"tt",  title:"Tetra Tower",         con:"Game Boy", year:1989, genre:"Puzzle",      players:"1-2", dev:"Octogon Soft",   pub:"Pocketworks", region:"World", mono:"TT", sky:"#6a7a2a", ground:"#3a4a1a",
    desc:"Apila bloques que caen y limpia líneas en este puzzle portátil adictivo. Modo maratón y duelo por cable." },
  { id:"mq",  title:"Moon Quest",          con:"Game Boy", year:1990, genre:"Aventura",    players:"1",   dev:"Aurora Works",   pub:"Pocketworks", region:"World", mono:"MQ", sky:"#4a5a2a", ground:"#2a3a1a",
    desc:"Una aventura monocroma bajo la luz lunar. Resuelve acertijos, dibuja tu propio mapa y descubre la verdad del cráter." },

  { id:"cf",  title:"Cyber Frog",          con:"PS1",      year:1998, genre:"RPG",         players:"1",   dev:"Lumen Studio",   pub:"Disco Nine",  region:"NTSC", mono:"CF", sky:"#3a2a5a", ground:"#2a1a4a",
    desc:"RPG con prerenderizados y batallas 3D tempranas. Una rana ciberpunk hackea su destino en una metrópolis lluviosa." },
  { id:"cb",  title:"Castle of Bones",     con:"PS1",      year:1999, genre:"Terror",      players:"1",   dev:"Blade Byte",     pub:"Disco Nine",  region:"NTSC", mono:"CB", sky:"#4a2a2a", ground:"#2a1414",
    desc:"Survival horror con cámaras fijas y ángulos cinematográficos. Recursos escasos, puzzles y un castillo que respira." },

  { id:"st",  title:"Star Pilot",          con:"Arcade",   year:1986, genre:"Shoot'em up", players:"1-2", dev:"Nova Lab",       pub:"CoinOp Intl", region:"World", mono:"SP", sky:"#1a2a5a", ground:"#3a2a6a",
    desc:"El recreativo de culto: scroll vertical, dificultad endiablada y un contador de monedas que nunca para. ¡Inserta crédito!" },
  { id:"ck",  title:"Crash Kart",          con:"Arcade",   year:1992, genre:"Carreras",    players:"1-4", dev:"Velocity X",     pub:"CoinOp Intl", region:"World", mono:"CK", sky:"#c4a02a", ground:"#6a4a1a",
    desc:"Cuatro jugadores, gabinete deluxe y derrapes imposibles. El party-racer que dominaba los salones recreativos." },
];
