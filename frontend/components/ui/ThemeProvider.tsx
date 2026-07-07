import React, { useEffect, useState } from 'react'

export default function ThemeProvider({ children }: { children: React.ReactNode }){
  const [theme, setTheme] = useState<'light'|'dark'>('light')
  useEffect(() => { document.documentElement.setAttribute('data-theme', theme) }, [theme])
  return (
    <div className={theme === 'dark' ? 'dark' : ''}>
      {children}
    </div>
  )
}
