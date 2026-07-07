import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import useAuth from '../../hooks/useAuth'
import Sidebar from '../../components/layout/Sidebar'
import TopNav from '../../components/layout/TopNav'

export default function DashboardPage() {
  const { user } = useAuth()
  const router = useRouter()
  useEffect(() => {
    if (!user) router.push('/auth/login')
  }, [user, router])

  return (
    <div className="min-h-screen flex">
      <Sidebar />
      <div className="flex-1 flex flex-col">
        <TopNav />
        <main className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="col-span-2 bg-white rounded-lg shadow p-6"> 
              <h3 className="text-lg font-semibold mb-2">Welcome back{user ? `, ${user.full_name || user.email}` : ''}</h3>
              <p className="text-sm text-slate-600">Start a new chat or continue your previous conversations.</p>
            </div>
            <div className="bg-white rounded-lg shadow p-6"> 
              <h4 className="text-md font-semibold mb-2">Stats</h4>
              <div className="text-sm text-slate-600">Active users, chats, and GPU status will appear here.</div>
            </div>
          </div>
        </main>
      </div>
    </div>
  )
}
