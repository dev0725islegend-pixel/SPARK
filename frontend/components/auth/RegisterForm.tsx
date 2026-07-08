import { useForm } from 'react-hook-form'
import { useRouter } from 'next/navigation'
import api from '../../lib/api'

export default function RegisterForm(){
  const { register, handleSubmit } = useForm()
  const router = useRouter()

  async function onSubmit(data:any){
    try{
      await api.post('/auth/register', { email: data.email, password: data.password, full_name: data.full_name })
      router.push('/auth/login')
    }catch(e){
      alert('Registration failed')
    }
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div>
        <label className="block text-sm font-medium">Full name</label>
        <input {...register('full_name')} className="mt-1 w-full border rounded p-2" />
      </div>
      <div>
        <label className="block text-sm font-medium">Email</label>
        <input {...register('email')} required className="mt-1 w-full border rounded p-2" />
      </div>
      <div>
        <label className="block text-sm font-medium">Password</label>
        <input {...register('password')} type="password" required className="mt-1 w-full border rounded p-2" />
      </div>
      <div className="flex items-center justify-between">
        <button type="submit" className="px-4 py-2 bg-primary text-white rounded">Create account</button>
      </div>
    </form>
  )
}
