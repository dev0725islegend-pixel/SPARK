import React from 'react'
import useAuth from '../../hooks/useAuth'

export default function TopNav(){
  const { user } = useAuth()
  return (
    <header className="flex items-center justify-between p-4 border-b bg-white">
      <div className="flex items-center gap-3">
        <div className="text-lg font-semibold">{user ? (user.full_name || user.email) : 'Guest'}</div>
      </div>
      <div className="flex items-center gap-3">
        <button className="px-3 py-1 rounded hover:bg-slate-50">Notifications</button>
        <button className="px-3 py-1 rounded hover:bg-slate-50">Profile</button>
      </div>
    </header>
  )
}
