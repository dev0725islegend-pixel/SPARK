import React from 'react'
import { Light as SyntaxHighlighter } from 'react-syntax-highlighter'
import ts from 'react-syntax-highlighter/dist/cjs/languages/hljs/typescript'
import { atomOneLight } from 'react-syntax-highlighter/dist/cjs/styles/hljs'

SyntaxHighlighter.registerLanguage('ts', ts)

export default function CodeBlock({ code, language='text' }: { code: string; language?: string }){
  return (
    <div className="relative">
      <div className="absolute right-2 top-2 flex gap-2">
        <button className="text-sm px-2 py-1 bg-white border rounded" onClick={() => { navigator.clipboard.writeText(code) }}>Copy</button>
        <a className="text-sm px-2 py-1 bg-white border rounded" href={`data:text/plain;charset=utf-8,${encodeURIComponent(code)}`} download={`code.${language}`}>Download</a>
      </div>
      <SyntaxHighlighter language={language} style={atomOneLight} showLineNumbers wrapLongLines>
        {code}
      </SyntaxHighlighter>
    </div>
  )
}
