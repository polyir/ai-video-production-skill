// Reusable Remotion 3D kit (from the first full-3D reel, Oct 2026). Change the Vazirmatn font name to your brand font.
// Rules: animate only from useCurrentFrame (no useFrame logic), text as canvas textures or HTML, render with --gl=angle.
import React, {Suspense, useEffect, useMemo, useState} from 'react';
import * as THREE from 'three';
import {ThreeElements, useThree} from '@react-three/fiber';
import {Billboard, Environment, Lightformer, RoundedBox, useGLTF} from '@react-three/drei';
import {Bloom, EffectComposer, ToneMapping, Vignette} from '@react-three/postprocessing';
import {ToneMappingMode} from 'postprocessing';
import {ThreeCanvas} from '@remotion/three';
import {continueRender, delayRender, staticFile, useCurrentFrame} from 'remotion';

export type V3 = [number, number, number];
export const lerp = (a: number, b: number, t: number) => a + (b - a) * t;
export const lerp3 = (a: V3, b: V3, t: number): V3 => [lerp(a[0], b[0], t), lerp(a[1], b[1], t), lerp(a[2], b[2], t)];
export const ease = (t: number) => (t <= 0 ? 0 : t >= 1 ? 1 : t * t * (3 - 2 * t));
export const mixHex = (a: string, b: string, t: number) => '#' + new THREE.Color(a).lerp(new THREE.Color(b), Math.max(0, Math.min(1, t))).getHexString();
export const fa = (n: number | string) => String(n).replace(/\d/g, (d) => '۰۱۲۳۴۵۶۷۸۹'[+d]);

// Camera set every frame from props (Remotion-safe).
export const Cam: React.FC<{p: V3; l: V3; fov?: number}> = ({p, l, fov = 35}) => {
  const {camera} = useThree();
  camera.position.set(...p);
  camera.lookAt(...l);
  const pc = camera as THREE.PerspectiveCamera;
  if (pc.fov !== fov) {
    pc.fov = fov;
    pc.updateProjectionMatrix();
  }
  return null;
};

// Hold the Remotion frame while a GLB is loading.
const Hold: React.FC = () => {
  const [h] = useState(() => delayRender('Loading GLB'));
  useEffect(() => () => continueRender(h), [h]);
  return null;
};
const GlbInner: React.FC<{src: string; tint?: number}> = ({src, tint = 0}) => {
  const {scene} = useGLTF(staticFile(src));
  const {advance} = useThree();
  useEffect(() => {
    const h = delayRender('GLB first paint');
    let raf = requestAnimationFrame(() => {
      advance(performance.now());
      raf = requestAnimationFrame(() => {
        advance(performance.now());
        continueRender(h);
      });
    });
    return () => {
      cancelAnimationFrame(raf);
      continueRender(h);
    };
  }, [advance]);
  const obj = useMemo(() => {
    const s = scene.clone(true);
    s.traverse((o) => {
      const m = o as THREE.Mesh;
      if (m.isMesh) {
        m.castShadow = true;
        m.receiveShadow = true;
        const mat = (m.material as THREE.MeshStandardMaterial).clone();
        mat.envMapIntensity = 1.1;
        m.material = mat;
      }
    });
    return s;
  }, [scene]);
  obj.traverse((o) => {
    const m = o as THREE.Mesh;
    if (m.isMesh) {
      const mat = m.material as THREE.MeshStandardMaterial;
      mat.emissive = new THREE.Color('#ff9a3c');
      mat.emissiveIntensity = tint;
    }
  });
  return <primitive object={obj} />;
};
export const Glb: React.FC<{src: string; tint?: number} & ThreeElements['group']> = ({src, tint, ...g}) => (
  <group {...g}>
    <Suspense fallback={<Hold />}>
      <GlbInner src={src} tint={tint} />
    </Suspense>
  </group>
);

// Canvas-texture with Persian text drawn per frame.
export const useCanvasTex = (w: number, h: number, draw: (c: CanvasRenderingContext2D) => void) => {
  const canvas = useMemo(() => {
    const c = document.createElement('canvas');
    c.width = w;
    c.height = h;
    return c;
  }, [w, h]);
  const tex = useMemo(() => {
    const t = new THREE.CanvasTexture(canvas);
    t.colorSpace = THREE.SRGBColorSpace;
    t.anisotropy = 8;
    return t;
  }, [canvas]);
  const ctx = canvas.getContext('2d')!;
  ctx.clearRect(0, 0, w, h);
  ctx.direction = 'rtl';
  draw(ctx);
  tex.needsUpdate = true;
  return tex;
};
export const txt = (c: CanvasRenderingContext2D, s: string, x: number, y: number, size: number, color: string, weight = 900, align: CanvasTextAlign = 'center') => {
  c.font = `${weight} ${size}px Vazirmatn`;
  c.fillStyle = color;
  c.textAlign = align;
  c.textBaseline = 'middle';
  c.fillText(s, x, y);
};
export const rr = (c: CanvasRenderingContext2D, x: number, y: number, w: number, h: number, r: number, fill: string, stroke?: string, lw = 4) => {
  c.beginPath();
  c.roundRect(x, y, w, h, r);
  c.fillStyle = fill;
  c.fill();
  if (stroke) {
    c.lineWidth = lw;
    c.strokeStyle = stroke;
    c.stroke();
  }
};

// A flat glass card (thin rounded box) with a canvas face.
export const Card: React.FC<{w: number; h: number; tex: THREE.Texture; edge?: string; glow?: number} & ThreeElements['group']> = ({w, h, tex, edge = '#ffb000', glow = 0.6, ...g}) => (
  <group {...g}>
    <RoundedBox args={[w, h, 0.06]} radius={0.05} smoothness={4}>
      <meshPhysicalMaterial color="#0b1420" roughness={0.25} metalness={0.2} clearcoat={1} emissive={edge} emissiveIntensity={glow * 0.15} transparent opacity={0.92} />
    </RoundedBox>
    <mesh position={[0, 0, 0.032]}>
      <planeGeometry args={[w * 0.96, h * 0.94]} />
      <meshBasicMaterial map={tex} transparent toneMapped={false} />
    </mesh>
  </group>
);

// Studio light rig without network HDRs (lightformers only).
export const Studio: React.FC<{warm?: number}> = ({warm = 0}) => (
  <Environment resolution={256} frames={1}>
    <Lightformer form="rect" intensity={2.2} position={[0, 4, 3]} scale={[8, 2, 1]} color="#dfe8ff" />
    <Lightformer form="rect" intensity={1.4} position={[-5, 1, 1]} rotation-y={Math.PI / 2} scale={[6, 3, 1]} color="#7fb2ff" />
    <Lightformer form="rect" intensity={1.6 + warm} position={[5, 0, 1]} rotation-y={-Math.PI / 2} scale={[6, 3, 1]} color="#ffb36b" />
    <Lightformer form="circle" intensity={1} position={[0, -3, 4]} scale={3} color="#ffffff" />
  </Environment>
);

// The EffectComposer is wired up after ThreeCanvas's own advance(); render twice more per frame so the
// post-processed image is what Remotion captures.
const Warmup: React.FC = () => {
  const {advance} = useThree();
  const frame = useCurrentFrame();
  useEffect(() => {
    const h = delayRender('post warmup');
    let raf = requestAnimationFrame(() => {
      advance(performance.now());
      raf = requestAnimationFrame(() => {
        advance(performance.now());
        continueRender(h);
      });
    });
    return () => {
      cancelAnimationFrame(raf);
      continueRender(h);
    };
  }, [frame, advance]);
  return null;
};

export const Post: React.FC<{bloom?: number; vignette?: number}> = ({bloom = 0.7, vignette = 0.55}) => (
  <EffectComposer multisampling={4}>
    <Bloom mipmapBlur intensity={bloom} luminanceThreshold={0.75} luminanceSmoothing={0.2} />
    <Vignette eskil={false} offset={0.25} darkness={vignette * 0.7} />
    <ToneMapping mode={ToneMappingMode.AGX} />
  </EffectComposer>
);

export const Stage: React.FC<{children: React.ReactNode; bg: string; fog?: [number, number]; bloom?: number; warm?: number}> = ({children, bg, fog, bloom, warm}) => (
  <ThreeCanvas width={1080} height={1920} shadows gl={{antialias: true, preserveDrawingBuffer: true}} camera={{fov: 35, near: 0.05, far: 200, position: [0, 0, 10]}}>
    <color attach="background" args={[bg]} />
    {fog ? <fog attach="fog" args={[bg, fog[0], fog[1]]} /> : null}
    <Studio warm={warm} />
    {children}
    {process.env.REMOTION_NOPOST ? null : <Post bloom={bloom} />}
    {process.env.REMOTION_NOPOST ? null : <Warmup />}
  </ThreeCanvas>
);

// Text label as a camera-facing canvas plane (drei <Html> is not reliable in renders).
export type LabelLine = {s: string; size: number; color: string; chip?: boolean};
export const Label3D: React.FC<{lines: LabelLine[]; w: number; opacity?: number; position?: V3}> = ({lines, w, opacity = 1, position = [0, 0, 0]}) => {
  const W = 1024;
  const H = Math.round(lines.reduce((a, l) => a + l.size * (l.chip ? 1.7 : 1.35), 0) + 40);
  const tex = useCanvasTex(W, H, (c) => {
    let y = 20;
    lines.forEach((l) => {
      const lh = l.size * (l.chip ? 1.7 : 1.35);
      c.font = `900 ${l.size}px Vazirmatn`;
      {
        c.lineJoin = 'round';
        c.lineWidth = l.size * 0.16;
        c.strokeStyle = 'rgba(3,7,11,.95)';
        c.textAlign = 'center';
        c.textBaseline = 'middle';
        c.strokeText(l.s, W / 2, y + lh / 2);
      }
      txt(c, l.s, W / 2, y + lh / 2, l.size, l.color);
      y += lh;
    });
  });
  return (
    <Billboard position={position}>
      <mesh>
        <planeGeometry args={[w, (w * H) / W]} />
        <meshBasicMaterial map={tex} transparent toneMapped={false} opacity={opacity} depthWrite={false} />
      </mesh>
    </Billboard>
  );
};

// Deterministic pseudo-random.
export const rnd = (i: number) => {
  const x = Math.sin(i * 127.1 + 311.7) * 43758.5453;
  return x - Math.floor(x);
};
