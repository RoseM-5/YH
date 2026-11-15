import { useEffect, useRef, useState } from 'react';
import StatusMark from './StatusMark';

export default function SceneStatusMark({ initialActive = false }) {
  const root = useRef(null);
  const [active, setActive] = useState(initialActive);

  useEffect(() => {
    const button = root.current?.closest('button');
    if (!button) return undefined;

    const sync = () => setActive(button.classList.contains('is-active'));
    sync();
    const observer = new MutationObserver(sync);
    observer.observe(button, { attributes: true, attributeFilter: ['class'] });
    return () => observer.disconnect();
  }, []);

  return (
    <span ref={root} className="yh-scene-status-inner">
      <StatusMark
        status={active ? 'running' : 'pending'}
        color={active ? '#0099ff' : '#bbd0de'}
        size={24}
        strokeWidth={2.2}
        dashes={8}
        spinDuration={1600}
        arcLength={0.64}
      />
    </span>
  );
}
