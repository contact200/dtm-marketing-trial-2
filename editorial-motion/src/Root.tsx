import React from 'react';
import {Composition, staticFile} from 'remotion';
import {EditorialMotionV1, EDITORIAL_MOTION_DEFAULTS} from './EditorialMotionV1';

// This composition is self-contained: it never reads existing trial/repo brand settings.
export const Root: React.FC = () => (
  <Composition
    id="EditorialMotionV1"
    component={EditorialMotionV1}
    durationInFrames={330}
    fps={30}
    width={1080}
    height={1920}
    defaultProps={{
      ...EDITORIAL_MOTION_DEFAULTS,
      photos: Array.from({length: 10}, (_, i) =>
        staticFile(`photos/${String(i + 1).padStart(2, '0')}.jpg`)
      ),
    }}
  />
);
