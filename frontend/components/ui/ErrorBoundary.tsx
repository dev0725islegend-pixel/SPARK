/** Simple error boundary for client components */
import React from 'react'

class ErrorBoundary extends React.Component<any, any> {
  constructor(props:any){ super(props); this.state = { hasError: false } }
  static getDerivedStateFromError(){ return { hasError: true } }
  componentDidCatch(error:any, info:any){ console.error('ErrorBoundary', error, info) }
  render(){
    if(this.state.hasError) return <div className="p-4 bg-red-50 text-red-800 rounded">Something went wrong.</div>
    return this.props.children
  }
}

export default ErrorBoundary
