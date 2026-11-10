import React from 'react'

/** Animated maliang mascot. Served from the Vite public dir (channel/web/static). */
const Mascot: React.FC<{ className?: string; alt?: string }> = ({
  className = 'h-48 w-auto',
  alt = 'maliang',
}) => (
  <img
    src="./mascot.gif"
    alt={alt}
    className={`mx-auto select-none pointer-events-none ${className}`}
    draggable={false}
  />
)

export default Mascot
