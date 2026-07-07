import React from 'react'
import ChatLayout from '../../../components/chat/ChatLayout'

interface Props {
  params: { id: string }
}

export default function ChatPage({ params }: Props) {
  return <ChatLayout conversationId={params.id} />
}
