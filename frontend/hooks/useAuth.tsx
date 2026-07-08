import { useContext } from 'react'
import { useUser } from '../components/auth/AuthProvider'

export default function useAuth(){
  const ctx = useUser()
  return ctx
}
