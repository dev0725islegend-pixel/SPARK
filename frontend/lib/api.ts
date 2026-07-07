const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

function defaultHeaders(){
  const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null
  return token ? { 'Authorization': `Bearer ${token}` } : {}
}

async function request(path:string, opts: RequestInit = {}){
  const res = await fetch(API + path, { ...opts, headers: { 'Content-Type': 'application/json', ...(opts.headers || {}), ...(defaultHeaders()) } })
  if(res.status === 401){
    // try refresh
    const refresh = localStorage.getItem('refresh_token')
    if(refresh){
      try{
        const r = await fetch(API + '/auth/refresh', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ refresh_token: refresh }) })
        if(r.ok){
          const j = await r.json()
          localStorage.setItem('access_token', j.access_token)
          // retry original
          const retry = await fetch(API + path, { ...opts, headers: { 'Content-Type': 'application/json', ...(opts.headers || {}), 'Authorization': `Bearer ${j.access_token}` } })
          return retry
        }
      }catch(e){ console.error('refresh failed', e) }
    }
  }
  return res
}

const api = {
  get: (path:string) => request(path, { method: 'GET' }),
  post: (path:string, body:any) => request(path, { method: 'POST', body: JSON.stringify(body) }),
  put: (path:string, body:any) => request(path, { method: 'PUT', body: JSON.stringify(body) }),
  delete: (path:string) => request(path, { method: 'DELETE' })
}

export default api
