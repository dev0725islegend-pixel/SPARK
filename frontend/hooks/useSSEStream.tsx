import { useState, useRef } from 'react'

export default function useSSEStream(){
  const controllerRef = useRef<AbortController | null>(null)
  const [status, setStatus] = useState<'idle'|'streaming'|'stopped'|'error'>('idle')

  function stopStream(){
    if(controllerRef.current){
      controllerRef.current.abort()
      controllerRef.current = null
    }
    setStatus('stopped')
  }

  async function startStream(payload:{ conversationId: string; content: string }, onChunk:(c:string)=>void, onDone?:()=>void, onError?: (e:any)=>void){
    stopStream()
    setStatus('streaming')
    const controller = new AbortController()
    controllerRef.current = controller
    try{
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/conversations/${payload.conversationId}/messages`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${localStorage.getItem('access_token')}` },
        body: JSON.stringify({ content: payload.content }),
        signal: controller.signal
      })
      if(!res.ok) throw new Error('Stream request failed: ' + res.status)
      const reader = res.body!.getReader()
      const decoder = new TextDecoder()
      let partial = ''
      while(true){
        const { done, value } = await reader.read()
        if(done) break
        const chunkText = decoder.decode(value, { stream: true })
        partial += chunkText
        // split by newline
        const parts = partial.split(/\n\n|\n/)
        partial = parts.pop() || ''
        for(const p of parts){
          const trimmed = p.trim()
          if(!trimmed) continue
          // sse starred events may come like: event: message\ndata: <token>\n
          // crude parsing: extract last content after 'data: '
          const dataMatch = trimmed.match(/data:\s*(.*)$/s)
          const text = dataMatch ? dataMatch[1] : trimmed
          onChunk(text)
        }
      }
      setStatus('idle')
      onDone && onDone()
    }catch(e){
      setStatus('error')
      onError && onError(e)
    }
  }

  return { startStream, stopStream, status }
}
