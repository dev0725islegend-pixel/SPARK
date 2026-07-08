import React, { useEffect, useRef, useState } from 'react'
import useSSEStream from '../../hooks/useSSEStream'
import MessageBubble from './MessageBubble'
import CodeBlock from './CodeBlock'

export default function ChatLayout({ conversationId }: { conversationId: string }){
  const [messages, setMessages] = useState<any[]>([])
  const [input, setInput] = useState('')
  const { startStream, stopStream, status } = useSSEStream()
  const containerRef = useRef<HTMLDivElement | null>(null)

  useEffect(() => {
    // load conversation messages
    async function load(){
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/conversations/${conversationId}`, { credentials: 'include' })
      if(res.ok){
        const json = await res.json()
        setMessages(json.messages || [])
      }
    }
    load()
  }, [conversationId])

  useEffect(() => { if(containerRef.current) containerRef.current.scrollTop = containerRef.current.scrollHeight }, [messages])

  async function send(){
    if(!input) return
    // append local user message
    const userMsg = { id: Date.now(), sender: 'user', content: input, created_at: new Date().toISOString() }
    setMessages(prev => [...prev, userMsg])
    setInput('')
    // start streaming
    const onChunk = (chunk:string) => {
      // append or update assistant typing bubble
      setMessages(prev => {
        const last = prev[prev.length - 1]
        if(last && last.sender === 'assistant' && last.streaming){
          const updated = [...prev]
          updated[updated.length -1] = { ...last, content: last.content + chunk }
          return updated
        }
        return [...prev, { id: Date.now()+Math.random(), sender: 'assistant', content: chunk, streaming: true }]
      })
    }
    const onDone = () => {
      setMessages(prev => prev.map(m => m.streaming ? { ...m, streaming: false } : m))
    }
    const onError = (e:any) => {
      setMessages(prev => [...prev, { id: Date.now(), sender: 'system', content: 'Error: ' + String(e) }])
    }
    startStream({ conversationId, content: userMsg.content }, onChunk, onDone, onError)
  }

  return (
    <div className="flex-1 flex flex-col">
      <div className="p-4 border-b bg-white">
        <h3 className="text-lg font-semibold">Conversation</h3>
      </div>
      <div className="flex-1 overflow-auto p-4" ref={containerRef}>
        <div className="space-y-4">
          {messages.map(m => (
            <MessageBubble key={m.id} message={m} />
          ))}
        </div>
      </div>
      <div className="p-4 bg-white border-t">
        <div className="flex gap-2">
          <textarea value={input} onChange={e => setInput(e.target.value)} className="flex-1 border rounded p-2" rows={2}></textarea>
          <div className="flex flex-col gap-2">
            <button onClick={send} className="px-4 py-2 bg-primary text-white rounded">Send</button>
            <button onClick={() => stopStream()} className="px-4 py-2 border rounded">Stop</button>
          </div>
        </div>
      </div>
    </div>
  )
}
