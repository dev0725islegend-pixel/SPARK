import Link from 'next/link'

export default function HomePage() {
  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="max-w-2xl w-full p-8">
        <h1 className="text-3xl font-semibold text-primary mb-4">SPARK AI Platform</h1>
        <p className="text-muted-foreground mb-6">Open-source AI platform for schools. Please sign in to continue.</p>
        <div className="flex gap-4">
          <Link href="/auth/login" className="px-4 py-2 bg-primary text-white rounded">Sign in</Link>
          <Link href="/auth/register" className="px-4 py-2 border border-slate-200 rounded">Register</Link>
        </div>
      </div>
    </div>
  )
}
