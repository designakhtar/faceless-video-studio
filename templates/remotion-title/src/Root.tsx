import React from 'react';
import {Composition} from 'remotion';
import {TitleCard} from './TitleCard';
export const Root: React.FC = () => (
  <Composition id="TitleCard" component={TitleCard} durationInFrames={90} fps={30}
    width={1920} height={1080}
    defaultProps={{title: 'Faceless Video Studio', subtitle: 'Remotion test', color: '#FFB347'}} />
);
