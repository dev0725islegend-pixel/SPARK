import React from 'react'
import Link from 'next/link'

export default function Sidebar(){
  return (
    <aside className="w-72 border-r bg-white h-screen p-4 sticky top-0">
      <div className="mb-6">
        <h2 className="text-xl font-semibold text-primary">SPARK</h2>
      </div>
      <nav className="space-y-2">
        <Link href="/dashboard" className="block py-2 px-3 rounded hover:bg-slate-50">Dashboard</Link>
        <Link href="/dashboard" className="block py-2 px-3 rounded hover:bg-slate-50">New Chat</Link>
        <Link href="/" className="block py-2 px-3 rounded hover:bg-slate-50">Chat History</Link>
        <Link href="/" className="block py-2 px-3 rounded hover:bg-slate-50">Settings</Link>
      </nav>
      <div className="mt-6">
        <button className="w-full py-2 bg-primary text-white rounded">New Chat</button>
      </div>
    </aside>
  )
}
