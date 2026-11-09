// Una sola composición: la lección descrita en public/piano.json (lo escribe strumenti/lezione.py).
import type { ReactNode } from 'react';
import { Composition, staticFile } from 'remotion';
import { Lezione } from './Lezione.tsx';

const durata = async () => {
  const piano = await (await fetch(staticFile('piano.json'))).json();
  return { durationInFrames: piano.durata_f, fps: piano.fps ?? 30 };
};

export function Radice(): ReactNode {
  return <Composition id="Lezione" component={Lezione} durationInFrames={300} fps={30} width={1920} height={1080} calculateMetadata={durata} />;
}
