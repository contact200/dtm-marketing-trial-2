/**
 * EditorialMotionV1 — reusable, image-driven, editorial kinetic type video.
 * Inspired by the visual grammar of the supplied 11-second reference video.
 * Not original proprietary source code from that advertisement.
 *
 * Remotion: 30 fps, 330 frames (11 seconds), designed for 1080x1920.
 * Place this in src/EditorialMotionV1.tsx and register the composition below.
 */
import React from 'react';
import {
  AbsoluteFill,
  Img,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';

export type EditorialMotionProps = {
  photos: string[]; // Public HTTPS or staticFile() image URLs; 6+ recommended
  brand?: string;
  greeting?: string;
  audience?: string;
  headline?: string;
  promise?: string;
  highlight?: string;
  feature?: string;
  finalWord?: string;
  palette?: Partial<{
    background: string;
    ink: string;
    accent: string;
    accentTint: string;
    dark: string;
    darkText: string;
  }>;
};

export const EDITORIAL_MOTION_DEFAULTS: Required<Omit<EditorialMotionProps, 'photos' | 'palette'>> = {
  brand: 'datethemoment',
  greeting: 'Hey,',
  audience: 'Coaches',
  headline: 'One game.',
  promise: 'Months of marketing.',
  highlight: 'Fully automated',
  feature: 'Captions · Scheduling · Posting',
  finalWord: 'Momentum',
};

const COLORS = {
  background: '#F5F5F2',
  ink: '#111217',
  accent: '#254CFF',
  accentTint: '#DDE4FF',
  dark: '#15161A',
  darkText: '#F7F6F2',
};

const CLAMP = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
const serif: React.CSSProperties = {fontFamily: 'Georgia, "Times New Roman", serif', letterSpacing: '-0.064em'};
const sans: React.CSSProperties = {fontFamily: 'Arial, Helvetica, sans-serif', letterSpacing: '-0.025em'};
const transition = (v: number, points: number[], output: number[]) =>
  interpolate(v, points, output, CLAMP);

const Photo: React.FC<{
  photos: string[];
  index: number;
  label?: string;
  style?: React.CSSProperties;
}> = ({photos, index, label, style}) => {
  const src = photos[index % Math.max(photos.length, 1)];
  return (
    <div style={{position: 'absolute', overflow: 'hidden', background: '#C2C4CB', ...style}}>
      {src ? (
        <Img src={src} style={{width: '100%', height: '100%', objectFit: 'cover'}} />
      ) : (
        <div style={{width: '100%', height: '100%', background: 'linear-gradient(130deg,#C8D2F1,#767C8B 52%,#1D2850)'}} />
      )}
      {label && (
        <div style={{position: 'absolute', bottom: 15, left: 16, fontSize: 17, color: '#fff', ...sans}}>
          {label}
        </div>
      )}
    </div>
  );
};

const MiniBrand: React.FC<{text: string; color: string; top?: number}> = ({text, color, top = 125}) => (
  <div style={{position: 'absolute', top, width: '100%', textAlign: 'center', color, fontSize: 28, fontWeight: 800, letterSpacing: '0.075em', ...sans}}>
    {text}
  </div>
);

const BrowserChrome: React.FC<{dark?: boolean}> = ({dark = false}) => (
  <div style={{height: 48, display: 'flex', alignItems: 'center', gap: 10, paddingLeft: 18, borderBottom: `1px solid ${dark ? '#45454B' : '#E3E3E4'}`}}>
    {['#FF6565', '#FFC66D', '#6FCC8A'].map((c, i) => (
      <div key={i} style={{width: 11, height: 11, borderRadius: '50%', background: c, opacity: 0.8}} />
    ))}
    <div style={{marginLeft: 32, height: 16, width: 360, borderRadius: 9, background: dark ? '#33343A' : '#E9E9EB'}} />
  </div>
);

const KineticIntro: React.FC<{
  f: number;
  greeting: string;
  audience: string;
  bg: string;
  ink: string;
}> = ({f, greeting, audience, bg, ink}) => {
  const greetingOpacity = transition(f, [0, 12, 26, 35], [0, 1, 1, 0]);
  const greetingY = transition(f, [0, 15], [36, 0]);
  const audienceX = transition(f, [24, 72], [950, -1150]);
  return (
    <AbsoluteFill style={{background: bg, justifyContent: 'center', alignItems: 'center'}}>
      <div style={{position: 'absolute', opacity: greetingOpacity, transform: `translateY(${greetingY}px)`, fontSize: 200, color: ink, ...serif}}>
        {greeting}
      </div>
      {f >= 24 && (
        <div style={{position: 'absolute', left: '50%', whiteSpace: 'nowrap', transform: `translateX(calc(-50% + ${audienceX}px))`, fontSize: 218, fontStyle: 'italic', color: ink, ...serif}}>
          {audience}
        </div>
      )}
    </AbsoluteFill>
  );
};

const OfferReveal: React.FC<{
  f: number;
  photos: string[];
  brand: string;
  headline: string;
  promise: string;
  accent: string;
  ink: string;
  bg: string;
  accentTint: string;
}> = ({f, photos, brand, headline, promise, accent, ink, bg, accentTint}) => {
  const enter = spring({frame: f, fps: 30, config: {damping: 22, stiffness: 100}});
  const zoom = transition(f, [0, 51], [1.08, 1]);
  return (
    <AbsoluteFill style={{background: bg, color: ink}}>
      <MiniBrand text={brand} color={accent} top={205} />
      <div style={{position: 'absolute', top: 370, width: '100%', textAlign: 'center', fontSize: 117, transform: `translateY(${(1 - enter) * 90}px)`, ...serif}}>
        {headline}
      </div>
      <Photo photos={photos} index={0} style={{left: 335, top: 575, width: 410, height: 620, transform: `scale(${zoom})`}} />
      <div style={{position: 'absolute', top: 1290, textAlign: 'center', width: '100%'}}>
        <span style={{fontSize: 75, background: accentTint, padding: '0px 22px 8px', fontStyle: 'italic', color: ink, ...serif}}>
          {promise}
        </span>
      </div>
      <div style={{position: 'absolute', top: 1450, width: '100%', textAlign: 'center', fontSize: 32, letterSpacing: '0.09em', textTransform: 'uppercase', ...sans}}>
        Photos to posts. Automatically.
      </div>
    </AbsoluteFill>
  );
};

const CollageMotion: React.FC<{
  f: number;
  photos: string[];
  promise: string;
  highlight: string;
  bg: string;
  ink: string;
  accentTint: string;
}> = ({f, photos, promise, highlight, bg, ink, accentTint}) => {
  const move = transition(f, [0, 59], [170, -65]);
  const bounce = (delay: number, amount: number) =>
    (1 - spring({frame: Math.max(0, f - delay), fps: 30, config: {damping: 20, stiffness: 125}})) * amount;
  return (
    <AbsoluteFill style={{background: bg, color: ink}}>
      <Photo photos={photos} index={1} style={{left: -80, top: 80, width: 430, height: 470, transform: `translate(${move}px,${bounce(0, -500)}px)`}} />
      <Photo photos={photos} index={2} style={{right: -60, top: 260, width: 360, height: 480, transform: `translate(${-move}px,${bounce(9, -520)}px)`}} />
      <Photo photos={photos} index={3} style={{left: -50, bottom: 155, width: 360, height: 490, transform: `translate(${move * 0.5}px,${bounce(14, 530)}px)`}} />
      <Photo photos={photos} index={4} style={{right: -30, bottom: 95, width: 360, height: 420, transform: `translate(${-move * 0.5}px,${bounce(19, 530)}px)`}} />
      <div style={{position: 'absolute', top: 805, width: '100%', textAlign: 'center', transform: `translateY(${bounce(12, 180)}px)`}}>
        <div style={{fontSize: 78, fontStyle: 'italic', ...serif}}><span style={{background: accentTint, padding: '0 19px'}}>{highlight}</span></div>
        <div style={{fontSize: 60, marginTop: 19, ...serif}}>{promise}</div>
      </div>
    </AbsoluteFill>
  );
};

const DarkProductReveal: React.FC<{
  f: number;
  photos: string[];
  brand: string;
  dark: string;
  darkText: string;
}> = ({f, photos, brand, dark, darkText}) => {
  const y = transition(f, [0, 18, 52], [1120, 120, -30]);
  return (
    <AbsoluteFill style={{background: '#B8B9BD'}}>
      <div style={{position: 'absolute', top: 155, left: 40, width: 1000, height: 1600, background: dark, color: darkText, transform: `translateY(${y}px)`, boxShadow: '0 26px 70px #0005', overflow: 'hidden'}}>
        <BrowserChrome dark />
        <div style={{fontSize: 95, color: '#DAC7E1', padding: '85px 65px 25px', ...serif}}>Your content, <i>organized.</i></div>
        <div style={{display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid #44454B', padding: '22px 65px 35px', fontSize: 23, textTransform: 'uppercase', letterSpacing: '0.08em', ...sans}}>
          <span>{brand}</span><span>Gallery&nbsp; / &nbsp;Calendar&nbsp; / &nbsp;Posts</span>
        </div>
        <div style={{position: 'relative', height: 1120}}>
          <Photo photos={photos} index={5} style={{left: 45, top: 70, width: 360, height: 480}} />
          <Photo photos={photos} index={3} style={{left: 455, top: 100, width: 445, height: 315}} />
          <Photo photos={photos} index={2} style={{left: 455, top: 445, width: 445, height: 570}} />
          <Photo photos={photos} index={1} style={{left: 45, top: 580, width: 360, height: 435}} />
        </div>
      </div>
    </AbsoluteFill>
  );
};

const LightProductReveal: React.FC<{
  f: number;
  photos: string[];
  bg: string;
  ink: string;
  accent: string;
}> = ({f, photos, bg, ink, accent}) => {
  const x = transition(f, [0, 13, 40], [1150, 0, -50]);
  return (
    <AbsoluteFill style={{background: '#D1D1D3'}}>
      <div style={{position: 'absolute', top: 220, left: 45, width: 1000, height: 1430, background: bg, transform: `translateX(${x}px)`, boxShadow: '0 20px 65px #0003', color: ink, overflow: 'hidden'}}>
        <BrowserChrome />
        <div style={{padding: '35px 55px', display: 'flex', justifyContent: 'space-between', fontSize: 23, ...sans}}><span>{'DATETHEMOMENT / STUDIO'}</span><span>Content library &nbsp; ◦ &nbsp; Schedule</span></div>
        <div style={{fontSize: 95, padding: '40px 60px 45px', ...serif}}>From gallery <i>to calendar.</i></div>
        <div style={{height: 7, width: 150, background: accent, marginLeft: 60}} />
        <div style={{position: 'relative', height: 900, marginTop: 50}}>
          <Photo photos={photos} index={2} style={{left: 35, top: 45, width: 290, height: 480}} />
          <Photo photos={photos} index={0} style={{left: 355, top: 45, width: 290, height: 480}} />
          <Photo photos={photos} index={4} style={{left: 675, top: 45, width: 290, height: 480}} />
          <div style={{position: 'absolute', top: 590, left: 55, fontSize: 37, ...sans}}>Scheduled for the next 30 days</div>
          {Array.from({length: 7}, (_, i) => (
            <div key={i} style={{position: 'absolute', top: 685, left: 55 + i * 130, width: 100, height: 110, background: i < 5 ? '#CBD3F7' : '#EEEFF2', display: 'flex', alignItems: 'center', justifyContent: 'center', color: ink, fontSize: 30, ...sans}}>{i + 1}</div>
          ))}
        </div>
      </div>
    </AbsoluteFill>
  );
};

const EndCard: React.FC<{f: number; bg: string; ink: string; accentTint: string; word: string}> = ({f, bg, ink, accentTint, word}) => {
  const lift = transition(f, [0, 16], [130, 0]);
  return (
    <AbsoluteFill style={{background: bg, color: ink, alignItems: 'center', justifyContent: 'center'}}>
      <div style={{textAlign: 'center', transform: `translateY(${lift}px)`}}>
        <div style={{fontSize: 39, textTransform: 'uppercase', letterSpacing: '0.16em', ...sans}}>MORE</div>
        <div style={{marginTop: 35, fontSize: 150, lineHeight: 1.05, fontStyle: 'italic', background: accentTint, padding: '0 35px 16px', ...serif}}>{word}</div>
      </div>
    </AbsoluteFill>
  );
};

/** Main component — pass publicly accessible image URLs via inputProps. */
export const EditorialMotionV1: React.FC<EditorialMotionProps> = (props) => {
  const colors = {...COLORS, ...props.palette};
  const copy = {...EDITORIAL_MOTION_DEFAULTS, ...props};
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  // Timeline is authored for 30fps; other rates scale automatically.
  const at30 = Math.round((frame * 30) / fps);
  // The frame-accurate local scene renderer works against a 30fps virtual timeline.
  // We supply local frames explicitly to each scene so other composition frame rates work.
  const section = (from: number, to: number, body: (f: number) => React.ReactNode) => {
    if (at30 < from || at30 > to) return null;
    const local = at30 - from;
    const fadeIn = transition(local, [0, 5], [0, 1]);
    const fadeOut = transition(local, [to - from - 6, to - from], [1, 0]);
    return <AbsoluteFill style={{opacity: fadeIn * fadeOut}}>{body(local)}</AbsoluteFill>;
  };
  return (
    <AbsoluteFill style={{background: colors.background, overflow: 'hidden'}}>
      {section(0, 84, (f) => <KineticIntro f={f} greeting={copy.greeting} audience={copy.audience} bg={colors.background} ink={colors.ink} />)}
      {section(80, 147, (f) => <OfferReveal f={f} photos={props.photos} brand={copy.brand} headline={copy.headline} promise={copy.promise} accent={colors.accent} ink={colors.ink} bg={colors.background} accentTint={colors.accentTint} />)}
      {section(143, 212, (f) => <CollageMotion f={f} photos={props.photos} promise={copy.promise} highlight={copy.highlight} bg={colors.background} ink={colors.ink} accentTint={colors.accentTint} />)}
      {section(207, 261, (f) => <DarkProductReveal f={f} photos={props.photos} brand={copy.brand} dark={colors.dark} darkText={colors.darkText} />)}
      {section(256, 296, (f) => <LightProductReveal f={f} photos={props.photos} bg={colors.background} ink={colors.ink} accent={colors.accent} />)}
      {section(292, 350, (f) => <EndCard f={f} bg={colors.background} ink={colors.ink} accentTint={colors.accentTint} word={copy.finalWord} />)}
    </AbsoluteFill>
  );
};

/**
 * Example registration in src/Root.tsx:
 *
 * import {Composition, staticFile} from 'remotion';
 * import {EditorialMotionV1} from './EditorialMotionV1';
 *
 * <Composition
 *   id="EditorialMotionV1"
 *   component={EditorialMotionV1}
 *   fps={30}
 *   durationInFrames={330}
 *   width={1080}
 *   height={1920}
 *   defaultProps={{photos: [
 *     staticFile('photos/01.jpg'), staticFile('photos/02.jpg'),
 *     staticFile('photos/03.jpg'), staticFile('photos/04.jpg'),
 *     staticFile('photos/05.jpg'), staticFile('photos/06.jpg'),
 *   ]}}
 * />
 *
 * For source-video-like 4:5 framing, change height to 1350 and
 * adjust y coordinates. Default is 9:16 for Instagram Reels.
 */