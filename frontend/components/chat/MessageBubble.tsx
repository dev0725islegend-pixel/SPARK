import React from 'react'
import CodeBlock from './CodeBlock'
import marked from 'marked'

function renderContent(content:string){
  // convert markdown to HTML and handle code blocks specially
  // For safety, keep it simple; in production use a sanitizer
  const html = marked.parse(content)
  return { __html: html }
}

export default function MessageBubble({ message }: { message: any }){
  const isUser = message.sender === 'user'
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div className={`max-w-[80%] p-3 rounded-lg ${isUser ? 'bg-primary text-white' : 'bg-slate-50 text-slate-900'}`}>
        <div dangerouslySetInnerHTML={renderContent(message.content || '')} />
        <div className="text-xs text-slate-400 mt-2">{new Date(message.created_at || Date.now()).toLocaleString()}</div>
      </div>
    </div>
  )
}
