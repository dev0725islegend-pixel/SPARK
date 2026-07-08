import React, { createContext, useContext, useEffect, useState } from 'react'
import api from '../../lib/api'

type User = { id: string; email: string; full_name?: string }

const AuthContext = createContext<any>(null)

export default function AuthProvider({ children }: { children: React.ReactNode }){
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function init(){
      const token = localStorage.getItem('access_token')
      if(!token){ setLoading(false); return }
      try{
        const res = await api.get('/users/me')
        const json = await res.json()
        setUser(json)
      }catch(e){
        console.error('Auth init failed', e)
      }finally{ setLoading(false) }
    }
    init()
  }, [])

  return (
    <AuthContext.Provider value={{ user, setUser, loading }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuthContext = () => useContext(AuthContext)

export function useUser(){ return useContext(AuthContext) }
