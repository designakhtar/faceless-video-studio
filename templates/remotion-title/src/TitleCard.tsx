import React from 'react';
import {AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
type Props = {title: string; subtitle: string; color: string};
export const TitleCard: React.FC<Props> = ({title, subtitle, color}) => {
  const f = useCurrentFrame(); const {fps} = useVideoConfig();
  const s = spring({frame: f, fps, config: {damping: 14}});
  const o = interpolate(f, [10, 30], [0, 1], {extrapolateRight: 'clamp'});
  return (
    <AbsoluteFill style={{background: 'transparent', justifyContent: 'center', alignItems: 'center', fontFamily: 'Arial, sans-serif'}}>
      <div style={{transform: `scale(${s})`, fontSize: 110, fontWeight: 800, color: 'white', textShadow: '0 8px 30px rgba(0,0,0,.6)'}}>{title}</div>
      <div style={{opacity: o, fontSize: 48, color, marginTop: 20}}>{subtitle}</div>
    </AbsoluteFill>
  );
};
