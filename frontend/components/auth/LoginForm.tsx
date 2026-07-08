import { useForm } from 'react-hook-form'
import { useRouter } from 'next/navigation'
import api from '../../lib/api'
import useAuth from '../../hooks/useAuth'

export default function LoginForm(){
  const { register, handleSubmit } = useForm()
  const router = useRouter()
  const { setUser } = useAuth()

  async function onSubmit(data:any){
    try{
      const res = await api.post('/auth/login', { email: data.email, password: data.password })
      const json = await res.json()
      // store tokens
      localStorage.setItem('access_token', json.access_token)
      localStorage.setItem('refresh_token', json.refresh_token)
      // fetch user
      const userRes = await api.get('/users/me')
      const userJson = await userRes.json()
      setUser(userJson)
      router.push('/dashboard')
    }catch(e){
      alert('Login failed')
    }
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div>
        <label className="block text-sm font-medium">Email</label>
        <input {...register('email')} required className="mt-1 w-full border rounded p-2" />
      </div>
      <div>
        <label className="block text-sm font-medium">Password</label>
        <input {...register('password')} type="password" required className="mt-1 w-full border rounded p-2" />
      </div>
      <div className="flex items-center justify-between">
        <button type="submit" className="px-4 py-2 bg-primary text-white rounded">Sign in</button>
      </div>
    </form>
  )
}
