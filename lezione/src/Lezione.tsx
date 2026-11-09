// La lección generada de Open Escool: fichas animadas a partir del guion.
// Todo viene de public/piano.json (strumenti/lezione.py): escenas con inicio y duración en fotogramas, para cada escena `m` (en qué
// fotograma de la escena cae cada {{marcador}} del guion), subtítulos, pasos, tema. Aquí no hay ningún tiempo escrito.
// Los tipos de escena son genéricos (apertura, confronto, settimana, punti, tabella, tempo, media, calcolo, riepilogo): un tema
// nuevo reutiliza los mismos, solo cambia el guion.
import type { CSSProperties, ReactNode } from 'react';
import { createContext, useContext, useEffect, useState } from 'react';
import {
  AbsoluteFill, cancelRender, continueRender, delayRender, Easing, Img, interpolate, Sequence, staticFile, useCurrentFrame,
} from 'remotion';

/* eslint-disable @typescript-eslint/no-explicit-any */
type Tema = { acc: string; fondo: string; carta: string; carta2: string; linea: string; testo: string; tenue: string; avviso: string; font: string };
const BASE: Tema = {
  acc: '#AFF320', fondo: '#0B0C0D', carta: '#111315', carta2: '#17191C', linea: '#26292C', testo: '#F2F2F0', tenue: '#9A9C9E',
  avviso: '#D8A35D', font: "'Geist Lezione', 'Helvetica Neue', Arial, sans-serif",
};
const TemaCtx = createContext<Tema>(BASE);
const useT = () => useContext(TemaCtx);

// dónde está la ficha en el fotograma 1920×1080
const SCHEDA = { x: 64, y: 100, w: 1420, h: 808 };
const PASSI = { x: 1524, y: 100, w: 332 };

const fissa = { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' } as const;

function rampa(f: number, da: number, durata: number): number {
  return interpolate(f, [da, da + Math.max(1, durata)], [0, 1], { ...fissa, easing: Easing.out(Easing.cubic) });
}

/** Entrada: de desenfocado a nítido, como en las guías aprobadas el 01/11. */
function dallaSfocata(f: number, da: number): CSSProperties {
  const t = f - da;
  const opacity = interpolate(t, [0, 6], [0, 1], fissa);
  const scala = interpolate(t, [0, 7], [1.05, 1], fissa);
  const blur = interpolate(t, [0, 14], [14, 0], fissa);
  return { opacity, transform: `scale(${scala.toFixed(4)})`, filter: blur > 0.05 ? `blur(${blur.toFixed(2)}px)` : undefined };
}

function Comparsa({ da, stile, children }: { da: number; stile?: CSSProperties; children: ReactNode }): ReactNode {
  const f = useCurrentFrame();
  if (f < da) return null;
  return <div style={{ ...stile, ...dallaSfocata(f, da) }}>{children}</div>;
}

const cue = (s: any, nome?: string) => (nome && s.m && s.m[nome] !== undefined ? s.m[nome] : 0);

// --- cargas ------------------------------------------------------------------------------------------------------------------------
function usePiano(): any {
  const [p, setP] = useState<any>(null);
  const [gancio] = useState(() => delayRender('piano'));
  useEffect(() => {
    fetch(staticFile('piano.json')).then((r) => r.json()).then((d) => { setP(d); continueRender(gancio); }).catch((e) => cancelRender(e));
  }, [gancio]);
  return p;
}

/** Geist (OFL, public/font/OFL-Geist.txt), la tipografía del sitio de Ismagit: solo se dibuja con la tipografía ya cargada. */
function useGeist(): boolean {
  const [pronto, setPronto] = useState(false);
  const [gancio] = useState(() => delayRender('geist'));
  useEffect(() => {
    const c = new FontFace('Geist Lezione', `url(${staticFile('font/geist-variable.woff2')}) format('woff2-variations')`, { weight: '100 900', style: 'normal', display: 'block' });
    c.load().then(() => { document.fonts.add(c); setPronto(true); continueRender(gancio); }).catch((e) => cancelRender(e));
  }, [gancio]);
  return pronto;
}

// --- iconos ------------------------------------------------------------------------------------------------------------------------
function Spunta({ corpo, colore }: { corpo: number; colore: string }): ReactNode {
  return <svg viewBox="0 0 24 24" width={corpo} height={corpo} style={{ flexShrink: 0 }} fill="none" stroke={colore} strokeWidth={3.2} strokeLinecap="round" strokeLinejoin="round"><path d="M4 12.5l5.2 5.2L20 6.5" /></svg>;
}
function Avviso({ corpo, colore }: { corpo: number; colore: string }): ReactNode {
  return (
    <svg viewBox="0 0 24 24" width={corpo} height={corpo} style={{ flexShrink: 0 }} fill="none" stroke={colore} strokeWidth={2.6} strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 3.5 L22 20.5 H2 Z" /><path d="M12 10v5" /><path d="M12 17.8v.2" />
    </svg>
  );
}
function Info({ corpo, colore }: { corpo: number; colore: string }): ReactNode {
  return (
    <svg viewBox="0 0 24 24" width={corpo} height={corpo} style={{ flexShrink: 0 }} fill="none" stroke={colore} strokeWidth={2.4} strokeLinecap="round">
      <circle cx="12" cy="12" r="9.5" /><path d="M12 11v6" /><path d="M12 7.6v.2" />
    </svg>
  );
}
function Documento({ corpo, colore }: { corpo: number; colore: string }): ReactNode {
  return (
    <svg viewBox="0 0 24 24" width={corpo} height={corpo} style={{ flexShrink: 0 }} fill="none" stroke={colore} strokeWidth={2} strokeLinecap="round" strokeLinejoin="round">
      <path d="M6 2.5h8l4.5 4.5V21.5H6z" /><path d="M14 2.5V7h4.5" /><path d="M9 12h6M9 15.5h6M9 19h4" />
    </svg>
  );
}

// --- piezas comunes ----------------------------------------------------------------------------------------------------------------
function Titolo({ testo }: { testo: string }): ReactNode {
  const T = useT();
  return (
    <Comparsa da={0} stile={{ position: 'absolute', left: 88, top: 70, right: 88 }}>
      <div style={{ width: 56, height: 6, borderRadius: 3, background: T.acc, marginBottom: 22 }} />
      <div style={{ fontSize: 58, fontWeight: 800, letterSpacing: -1.2, lineHeight: 1.06, color: T.testo }}>{testo}</div>
    </Comparsa>
  );
}

function Pillola({ testo, piena = false }: { testo: string; piena?: boolean }): ReactNode {
  const T = useT();
  return (
    <span style={{ display: 'inline-block', padding: '10px 22px', borderRadius: 999, fontSize: 26, fontWeight: 700, whiteSpace: 'nowrap',
      color: piena ? T.fondo : T.acc, background: piena ? T.acc : 'transparent', border: `2px solid ${T.acc}` }}>{testo}</span>
  );
}

function Nota({ s, nota, basso = 64, nelFlusso = false }: { s: any; nota?: any; basso?: number; nelFlusso?: boolean }): ReactNode {
  const T = useT();
  if (!nota) return null;
  const col = nota.avviso ? T.avviso : T.acc;
  return (
    <Comparsa da={cue(s, nota.cue)} stile={nelFlusso ? {} : { position: 'absolute', left: 88, right: 88, bottom: basso }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 20, padding: '24px 30px', borderRadius: 18, fontSize: 32, fontWeight: 600, lineHeight: 1.25,
        background: `${col}1A`, border: `2px solid ${col}66`, color: T.testo }}>
        {nota.avviso ? <Avviso corpo={40} colore={col} /> : <Info corpo={40} colore={col} />}<span>{nota.testo}</span>
      </div>
    </Comparsa>
  );
}

// --- las escenas -------------------------------------------------------------------------------------------------------------------
function Apertura({ s }: { s: any }): ReactNode {
  const T = useT();
  const f = useCurrentFrame();
  const x = s.schermo;
  const giro = interpolate(f, [0, s.durata_f], [0, 18], fissa);
  return (
    <>
      <svg width={700} height={700} viewBox="0 0 700 700" style={{ position: 'absolute', right: -170, top: 40, opacity: 0.16 * rampa(f, 0, 30) }}>
        <g transform={`rotate(${giro} 350 350)`} fill="none" stroke={T.acc}>
          {[300, 240, 180, 120].map((r, i) => <circle key={r} cx={350} cy={350} r={r} strokeWidth={2 + i} strokeDasharray={i % 2 ? '6 14' : undefined} />)}
        </g>
      </svg>
      <div style={{ position: 'absolute', left: 96, top: 170, right: 360 }}>
        <Comparsa da={0}><div style={{ fontSize: 26, fontWeight: 700, letterSpacing: 4, textTransform: 'uppercase', color: T.acc }}>{x.sopra}</div></Comparsa>
        <Comparsa da={cue(s, 'titolo') + 4}><div style={{ fontSize: 120, fontWeight: 800, letterSpacing: -4, lineHeight: 1.0, marginTop: 30 }}>{x.titolo}</div></Comparsa>
        <Comparsa da={cue(s, 'titolo') + 14}><div style={{ fontSize: 52, fontWeight: 500, color: T.tenue, marginTop: 26, letterSpacing: -0.5 }}>{x.sotto}</div></Comparsa>
      </div>
      <Comparsa da={cue(s, 'fonti')} stile={{ position: 'absolute', left: 96, bottom: 78, display: 'flex', alignItems: 'center', gap: 16, fontSize: 28, fontWeight: 600, color: T.tenue }}>
        <Documento corpo={36} colore={T.acc} />{x.fonti}
      </Comparsa>
    </>
  );
}

function Confronto({ s }: { s: any }): ReactNode {
  const T = useT();
  const f = useCurrentFrame();
  const x = s.schermo;
  return (
    <>
      <Titolo testo={x.titolo} />
      {/* columnas y aviso en el flujo: una columna que salta de línea empuja el aviso hacia abajo en vez de taparlo */}
      <div style={{ position: 'absolute', left: 88, right: 88, top: 240, display: 'flex', flexDirection: 'column', gap: 36 }}>
      <div style={{ display: 'flex', gap: 40 }}>
        {x.colonne.map((c: any) => {
          const pill = c.pillola && f >= cue(s, c.pillola.cue);
          return (
            <Comparsa key={c.nome} da={cue(s, c.cue)} stile={{ flex: 1 }}>
              <div style={{ position: 'relative', background: T.carta2, border: `2px solid ${pill ? T.acc : T.linea}`, borderRadius: 24, padding: '40px 44px', minHeight: 340, height: '100%', boxSizing: 'border-box',
                boxShadow: pill ? `0 0 40px ${T.acc}22` : undefined }}>
                <div style={{ fontSize: 46, fontWeight: 800, letterSpacing: -0.8 }}>{c.nome}</div>
                {c.righe.map((r: string) => (
                  <div key={r} style={{ display: 'flex', alignItems: 'center', gap: 16, fontSize: 31, color: T.tenue, marginTop: 20, fontWeight: 500 }}>
                    <div style={{ width: 9, height: 9, borderRadius: 5, background: T.tenue, flexShrink: 0 }} />{r}
                  </div>
                ))}
                {c.pillola ? <Comparsa da={cue(s, c.pillola.cue)} stile={{ marginTop: 28 }}><Pillola testo={c.pillola.testo} piena /></Comparsa> : null}
              </div>
            </Comparsa>
          );
        })}
      </div>
      <Nota s={s} nota={x.nota} nelFlusso />
      </div>
    </>
  );
}

// «Etiqueta: valor» en dos líneas: la etiqueta pequeña arriba, la cuenta grande abajo (una sola línea no cabe a la derecha del gráfico)
function Diviso({ testo, colore }: { testo: string; colore: string }): ReactNode {
  const T = useT();
  const i = testo.indexOf(': ');
  if (i < 0) return <div style={{ fontSize: 30, fontWeight: 700, lineHeight: 1.25, color: colore }}>{testo}</div>;
  return (
    <div>
      <div style={{ fontSize: 25, fontWeight: 600, color: T.tenue, letterSpacing: 0.2 }}>{testo.slice(0, i)}</div>
      <div style={{ marginTop: 6, fontSize: 40, fontWeight: 800, color: colore, whiteSpace: 'nowrap', letterSpacing: -0.5 }}>{testo.slice(i + 2)}</div>
    </div>
  );
}

function Settimana({ s }: { s: any }): ReactNode {
  const T = useT();
  const f = useCurrentFrame();
  const x = s.schermo;
  const b = x.budget as number;
  const max = 2 * b;
  const ALTO = 320, BASE_Y = 604, SX = 200, LARGO_BARRA = 80, PASSO = 112;
  const y = (v: number) => BASE_Y - (v / (max * 1.12)) * ALTO;
  const cB = cue(s, x.cue_barre), cD = cue(s, x.doppio?.cue), cS = cue(s, x.settimana?.cue);
  const doppio = f >= cD;
  const somma = x.spesa.reduce((a: number, v: number, i: number) => a + v * rampa(f, cB + i * 6, 14), 0);
  const fineX = SX + PASSO * 6 + LARGO_BARRA;
  return (
    <>
      <Titolo testo={x.titolo} />
      {x.media ? <Comparsa da={cue(s, x.media.cue)} stile={{ position: 'absolute', left: 88, top: 188 }}><Pillola testo={x.media.testo} /></Comparsa> : null}
      {/* líneas: media y doble */}
      <Comparsa da={cB} stile={{ position: 'absolute', left: SX - 20, top: y(b), width: fineX - SX + 40, height: 0, borderTop: `3px dashed ${T.tenue}` }}>
        <span style={{ position: 'absolute', right: fineX - SX + 52, top: -19, fontSize: 26, fontWeight: 700, color: T.tenue, whiteSpace: 'nowrap' }}>{b} {x.valuta}</span>
      </Comparsa>
      {doppio ? (
        <div style={{ position: 'absolute', left: SX - 20, top: y(max), width: (fineX - SX + 40) * rampa(f, cD, 18), height: 0, borderTop: `3px solid ${T.acc}` }}>
          <span style={{ position: 'absolute', left: -96, top: -19, fontSize: 26, fontWeight: 800, color: T.acc, whiteSpace: 'nowrap', opacity: rampa(f, cD + 10, 8) }}>{max} {x.valuta}</span>
        </div>
      ) : null}
      {x.spesa.map((v: number, i: number) => {
        const k = rampa(f, cB + i * 6, 14);
        const h = (BASE_Y - y(v)) * k;
        const accesa = doppio && v >= max;
        return (
          <div key={i}>
            <div style={{ position: 'absolute', left: SX + i * PASSO, top: BASE_Y - h, width: LARGO_BARRA, height: h, borderRadius: '12px 12px 4px 4px',
              background: accesa ? T.acc : '#3A3F44', boxShadow: accesa ? `0 0 34px ${T.acc}66` : undefined }} />
            <div style={{ position: 'absolute', left: SX + i * PASSO - 10, width: LARGO_BARRA + 20, top: BASE_Y - h - 44, textAlign: 'center', fontSize: 26, fontWeight: 700,
              color: accesa ? T.acc : T.testo, opacity: rampa(f, cB + i * 6 + 8, 8) }}>
              <span style={{ background: T.carta, padding: '0 6px', borderRadius: 6 }}>{v} {x.valuta}</span>
            </div>
            <div style={{ position: 'absolute', left: SX + i * PASSO - 10, width: LARGO_BARRA + 20, top: BASE_Y + 14, textAlign: 'center', fontSize: 25, fontWeight: 600, color: T.tenue,
              opacity: rampa(f, cB, 10) }}>{x.giorni[i]}</div>
          </div>
        );
      })}
      {x.doppio ? <Comparsa da={cD + 6} stile={{ position: 'absolute', left: 1010, top: 262, width: 370 }}><Diviso testo={x.doppio.testo} colore={T.acc} /></Comparsa> : null}
      {x.settimana ? (
        <Comparsa da={cS} stile={{ position: 'absolute', left: 1010, top: 410, width: 370 }}>
          <Diviso testo={x.settimana.testo} colore={T.testo} />
          <div style={{ marginTop: 22, height: 18, borderRadius: 9, background: T.linea, overflow: 'hidden' }}>
            <div style={{ width: `${Math.min(100, (somma / (7 * b)) * 100)}%`, height: '100%', background: T.acc, borderRadius: 9 }} />
          </div>
          <div style={{ marginTop: 12, fontSize: 26, color: T.tenue, fontWeight: 600 }}>{Math.round(somma)} / {7 * b} {x.valuta}</div>
        </Comparsa>
      ) : null}
      {x.manager ? <Nota s={s} nota={{ cue: x.manager.cue, testo: x.manager.testo }} basso={48} /> : null}
    </>
  );
}

function Punti({ s }: { s: any }): ReactNode {
  const T = useT();
  const f = useCurrentFrame();
  const x = s.schermo;
  const ultima = [...x.righe].reverse().find((r: any) => f >= cue(s, r.cue));
  return (
    <>
      <Titolo testo={x.titolo} />
      <div style={{ position: 'absolute', left: 88, right: 88, top: 250, display: 'flex', flexDirection: 'column', gap: 30 }}>
        {x.righe.map((r: any) => {
          const col = r.icona === 'avviso' ? T.avviso : T.acc;
          const attiva = r === ultima;
          return (
            <Comparsa key={r.testo} da={cue(s, r.cue)}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 26, padding: '30px 34px', borderRadius: 20, background: T.carta2,
                border: `2px solid ${attiva ? col : T.linea}`, fontSize: 36, fontWeight: 600, lineHeight: 1.25, opacity: attiva ? 1 : 0.62 }}>
                {r.icona === 'avviso' ? <Avviso corpo={46} colore={col} /> : r.icona === 'spunta' ? <Spunta corpo={46} colore={col} /> : <Info corpo={46} colore={col} />}
                <span>{r.testo}</span>
              </div>
            </Comparsa>
          );
        })}
      </div>
    </>
  );
}

function Tabella({ s }: { s: any }): ReactNode {
  const T = useT();
  const x = s.schermo;
  const COL = '300px 1fr 1fr';
  return (
    <>
      <Titolo testo={x.titolo} />
      <div style={{ position: 'absolute', left: 88, right: 88, top: 250 }}>
        <Comparsa da={0}>
          <div style={{ display: 'grid', gridTemplateColumns: COL, padding: '0 30px 14px', fontSize: 23, fontWeight: 700, letterSpacing: 3, textTransform: 'uppercase', color: T.tenue }}>
            {x.intestazione.map((h: string) => <div key={h}>{h}</div>)}
          </div>
        </Comparsa>
        {x.righe.map((r: any) => (
          <Comparsa key={r.celle[0]} da={cue(s, r.cue)}>
            <div style={{ display: 'grid', gridTemplateColumns: COL, alignItems: 'center', padding: '26px 30px', marginTop: 14, borderRadius: 18, background: T.carta2,
              border: `2px solid ${T.linea}`, fontSize: 34, fontWeight: 600 }}>
              <div style={{ fontWeight: 800 }}>{r.celle[0]}</div>
              <div style={{ color: T.tenue }}>{r.celle[1]}</div>
              <div style={{ color: T.acc, fontWeight: 700 }}>{r.celle[2]}</div>
            </div>
          </Comparsa>
        ))}
      </div>
      <Nota s={s} nota={x.nota} />
    </>
  );
}

function Tempo({ s }: { s: any }): ReactNode {
  const T = useT();
  const f = useCurrentFrame();
  const x = s.schermo;
  const n = x.eventi.length;
  const SX = 290, FX = 1130, LY = 400;
  const px = (i: number) => (n === 1 ? SX : SX + ((FX - SX) * i) / (n - 1));
  // la línea llega al nodo cuando la voz lo nombra
  let fino = 0;
  x.eventi.forEach((e: any, i: number) => { if (f >= cue(s, e.cue)) fino = i === 0 ? SX : px(i - 1) + (px(i) - px(i - 1)) * rampa(f, cue(s, e.cue), 16); });
  return (
    <>
      <Titolo testo={x.titolo} />
      <div style={{ position: 'absolute', left: SX, top: LY - 2, width: FX - SX, height: 4, background: T.linea, borderRadius: 2 }} />
      <div style={{ position: 'absolute', left: SX, top: LY - 2, width: Math.max(0, fino - SX), height: 4, background: T.acc, borderRadius: 2 }} />
      {x.eventi.map((e: any, i: number) => (
        <Comparsa key={e.data} da={cue(s, e.cue)} stile={{ position: 'absolute', left: px(i) - 190, top: LY - 110, width: 380, textAlign: 'center' }}>
          <div style={{ fontSize: 38, fontWeight: 800, color: e.oggi ? T.acc : T.testo, letterSpacing: -0.5 }}>{e.data}</div>
          <div style={{ width: 30, height: 30, borderRadius: 15, margin: '38px auto 0', background: e.oggi ? T.acc : T.fondo, border: `4px solid ${T.acc}`,
            boxShadow: e.oggi ? `0 0 24px ${T.acc}88` : undefined }} />
          <div style={{ marginTop: 34, fontSize: 28, fontWeight: 600, lineHeight: 1.3, color: T.testo, background: T.carta2, border: `2px solid ${T.linea}`, borderRadius: 16,
            padding: '20px 22px' }}>{e.testo}</div>
        </Comparsa>
      ))}
      <Nota s={s} nota={x.nota} />
    </>
  );
}

function hashino(i: number): number {
  const v = Math.sin(i * 12.9898 + 4.1) * 43758.5453;
  return v - Math.floor(v);
}

function Media({ s }: { s: any }): ReactNode {
  const T = useT();
  const f = useCurrentFrame();
  const x = s.schermo;
  const vals: number[] = x.punti;
  const lo = Math.floor((Math.min(...vals, x.target.valore) - 10) / 10) * 10;
  const hi = Math.ceil((Math.max(...vals, x.target.valore) + 10) / 10) * 10;
  const SX = 140, FX = 1280, AY = 560;
  const px = (v: number) => SX + ((v - lo) / (hi - lo)) * (FX - SX);
  const media = vals.reduce((a, v) => a + v, 0) / vals.length;
  const cT = cue(s, x.target.cue), cP = cue(s, x.cue_punti), cR = cue(s, x.risultato?.cue);
  const tacche = [];
  for (let v = lo; v <= hi; v += 10) tacche.push(v);
  return (
    <>
      <Titolo testo={x.titolo} />
      <div style={{ position: 'absolute', left: SX, top: AY, width: FX - SX, height: 3, background: T.linea }} />
      {tacche.map((v) => (
        <div key={v} style={{ position: 'absolute', left: px(v) - 40, width: 80, top: AY + 16, textAlign: 'center', fontSize: 24, color: T.tenue, fontWeight: 600 }}>{v} {x.valuta}</div>
      ))}
      <Comparsa da={cT} stile={{ position: 'absolute', left: px(x.target.valore) - 2, top: 270, height: AY - 270, borderLeft: `4px dashed ${T.acc}` }}>
        {/* el objetivo a la izquierda de su línea, la media real a la derecha de la suya: arriba, sobre los puntos, sin tocarse */}
        <div style={{ position: 'absolute', right: 22, top: -6, fontSize: 28, fontWeight: 800, color: T.acc, whiteSpace: 'nowrap' }}>{x.target.testo}</div>
      </Comparsa>
      {vals.map((v, i) => {
        const da = cP + i * 4;
        if (f < da) return null;
        const sopra = v > x.target.valore;
        const yy = 330 + hashino(i) * 170;
        return (
          <div key={i} style={{ position: 'absolute', left: px(v) - 17, top: yy, width: 34, height: 34, borderRadius: 17, background: sopra ? T.avviso : T.acc,
            opacity: 0.92 * rampa(f, da, 6), transform: `scale(${(0.4 + 0.6 * rampa(f, da, 8)).toFixed(3)})` }} />
        );
      })}
      {x.risultato ? (
        <Comparsa da={cR} stile={{ position: 'absolute', left: px(media) - 2, top: 270, height: AY - 270, borderLeft: `4px solid ${T.testo}` }}>
          <div style={{ position: 'absolute', left: 18, top: -6, fontSize: 28, fontWeight: 800, color: T.testo, whiteSpace: 'nowrap' }}>
            {x.risultato.etichetta ?? '≈'} {Math.round(media)} {x.valuta}
          </div>
        </Comparsa>
      ) : null}
      {x.risultato ? <Nota s={s} nota={{ cue: x.risultato.cue, testo: x.risultato.testo, avviso: true }} basso={48} /> : null}
    </>
  );
}

function Calcolo({ s }: { s: any }): ReactNode {
  const T = useT();
  const x = s.schermo;
  return (
    <>
      <Titolo testo={x.titolo} />
      <div style={{ position: 'absolute', left: 88, top: 250, width: 900 }}>
        {x.righe.map((r: any, i: number) => (
          <Comparsa key={r.etichetta} da={cue(s, r.cue) + (i > 0 && x.righe[i - 1].cue === r.cue ? 12 : 0)}>
            <div style={{ display: 'flex', alignItems: 'baseline', justifyContent: 'space-between', padding: r.evidenzia ? '30px 0 0' : '18px 0',
              marginTop: r.evidenzia ? 18 : 0, borderTop: r.evidenzia ? `3px solid ${T.acc}` : `2px solid ${T.linea}`,
              fontSize: r.evidenzia ? 46 : 38, fontWeight: r.evidenzia ? 800 : 600, color: r.evidenzia ? T.acc : T.testo }}>
              <span>{r.etichetta}</span><span style={{ fontSize: r.evidenzia ? 72 : 46, fontWeight: 800 }}>{r.valore}</span>
            </div>
          </Comparsa>
        ))}
      </div>
      <Nota s={s} nota={x.nota} />
    </>
  );
}

function Riepilogo({ s }: { s: any }): ReactNode {
  const T = useT();
  const x = s.schermo;
  const ultimo = Math.max(...x.righe.map((r: any) => cue(s, r.cue)));
  return (
    <>
      <Titolo testo={x.titolo} />
      <div style={{ position: 'absolute', left: 88, right: 88, top: 236, display: 'flex', flexDirection: 'column', gap: 20 }}>
        {x.righe.map((r: any) => (
          <Comparsa key={r.testo} da={cue(s, r.cue)}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 26, fontSize: 38, fontWeight: 700, lineHeight: 1.2, padding: '20px 30px', borderRadius: 18, background: T.carta2,
              border: `2px solid ${T.linea}` }}>
              <Spunta corpo={48} colore={T.acc} /><span>{r.testo}</span>
            </div>
          </Comparsa>
        ))}
        {x.sotto ? <Comparsa da={ultimo + 75} stile={{ marginTop: 18, fontSize: 32, fontWeight: 700, color: T.acc }}>{x.sotto} →</Comparsa> : null}
      </div>
    </>
  );
}

const SCENE: Record<string, (p: { s: any }) => ReactNode> = {
  apertura: Apertura, confronto: Confronto, settimana: Settimana, punti: Punti, tabella: Tabella, tempo: Tempo, media: Media, calcolo: Calcolo, riepilogo: Riepilogo,
};

/** Una escena dentro de la ficha: entra desenfocada y sale con un fundido en los últimos fotogramas. */
function Scena({ s }: { s: any }): ReactNode {
  const f = useCurrentFrame();
  const C = SCENE[s.tipo] ?? Punti;
  const esce = interpolate(f, [s.durata_f - 9, s.durata_f], [1, 0], fissa);
  return <AbsoluteFill style={{ opacity: esce }}><C s={s} /></AbsoluteFill>;
}

// --- marco: barra arriba, pasos a la derecha, subtítulos abajo ---------------------------------------------------------------------
function Passi({ p, attivo }: { p: any; attivo: number }): ReactNode {
  const T = useT();
  return (
    <div style={{ position: 'absolute', left: PASSI.x, top: PASSI.y, width: PASSI.w }}>
      <div style={{ fontSize: 18, letterSpacing: 4, color: T.tenue, fontWeight: 700, marginBottom: 18, textTransform: 'uppercase' }}>{p.etichetta_passi}</div>
      {p.passi.map((nome: string, i: number) => {
        const a = i === attivo;
        const fatto = i < attivo;
        return (
          <div key={nome} style={{ borderLeft: `4px solid ${a || fatto ? T.acc : T.linea}`, padding: '14px 14px 15px 18px', marginBottom: 10, borderRadius: 4,
            background: a ? T.carta2 : 'transparent' }}>
            <div style={{ fontSize: 25, fontWeight: a ? 800 : 600, color: a ? T.testo : fatto ? T.tenue : '#5E6164', lineHeight: 1.2 }}>{nome}</div>
          </div>
        );
      })}
    </div>
  );
}

function Sottotitoli({ pezzi }: { pezzi: any[] }): ReactNode {
  const T = useT();
  const f = useCurrentFrame();
  const p = pezzi.find((x) => f >= x.da_f && f < x.a_f);
  if (!p) return null;
  const e = interpolate(f - p.da_f, [0, 4], [0, 1], fissa);
  return (
    <div style={{ position: 'absolute', left: SCHEDA.x, top: SCHEDA.y + SCHEDA.h + 14, width: SCHEDA.w, height: 140, display: 'flex', alignItems: 'center', justifyContent: 'center',
      textAlign: 'center', fontSize: 36, fontWeight: 600, color: T.testo, lineHeight: 1.25, opacity: e, padding: '0 40px', boxSizing: 'border-box' }}>{p.testo}</div>
  );
}

function Cornice({ p }: { p: any }): ReactNode {
  const T = useT();
  const f = useCurrentFrame();
  const adesso = [...p.scene].reverse().find((s: any) => f >= s.da_f) ?? p.scene[0];
  return (
    <>
      <div style={{ position: 'absolute', left: SCHEDA.x + 4, top: 34, display: 'flex', alignItems: 'center', gap: 14, fontSize: 22, fontWeight: 600, color: T.tenue, letterSpacing: 0.2 }}>
        <div style={{ width: 12, height: 12, borderRadius: 6, background: T.acc, boxShadow: `0 0 12px ${T.acc}` }} />
        <b style={{ color: T.testo, fontWeight: 800, letterSpacing: 2.5, textTransform: 'uppercase', fontSize: 20 }}>{p.marchio}</b>
        <span>·</span><span>{p.percorso}</span>
      </div>
      <div style={{ position: 'absolute', left: SCHEDA.x, top: SCHEDA.y, width: SCHEDA.w, height: SCHEDA.h, background: T.carta, borderRadius: 30,
        border: `1px solid ${T.linea}`, boxShadow: '0 30px 80px rgba(0,0,0,.45)' }} />
      <Passi p={p} attivo={adesso.passo} />
      <div style={{ position: 'absolute', left: PASSI.x, top: 990, width: PASSI.w, display: 'flex', alignItems: 'center', gap: 12, fontSize: 19, fontWeight: 600, color: T.tenue }}>
        {p.crediti}<Img src={staticFile('marca/ismagit-bianco.png')} style={{ height: 24 }} />
      </div>
    </>
  );
}

function Corpo({ p }: { p: any }): ReactNode {
  const T = useT();
  return (
    <AbsoluteFill style={{ background: `radial-gradient(1200px 700px at 30% -10%, ${T.acc}14, transparent 70%), ${T.fondo}`, fontFamily: T.font, color: T.testo }}>
      <Cornice p={p} />
      <div style={{ position: 'absolute', left: SCHEDA.x, top: SCHEDA.y, width: SCHEDA.w, height: SCHEDA.h, overflow: 'hidden', borderRadius: 30 }}>
        {p.scene.map((s: any) => (
          <Sequence key={s.id} from={s.da_f} durationInFrames={s.durata_f} layout="none">
            <div style={{ position: 'absolute', inset: 0 }}><Scena s={s} /></div>
          </Sequence>
        ))}
      </div>
      <Sottotitoli pezzi={p.sottotitoli} />
    </AbsoluteFill>
  );
}

export function Lezione(): ReactNode {
  const p = usePiano();
  const pronto = useGeist();
  if (!p || !pronto) return null;
  return <TemaCtx.Provider value={{ ...BASE, ...(p.tema ?? {}) }}><Corpo p={p} /></TemaCtx.Provider>;
}
