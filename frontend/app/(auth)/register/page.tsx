import RegisterForm from '../../../components/auth/RegisterForm'

export default function RegisterPage() {
  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="w-full max-w-md bg-white rounded-xl shadow p-6">
        <h2 className="text-2xl font-semibold mb-4">Create an account</h2>
        <RegisterForm />
      </div>
    </div>
  )
}
