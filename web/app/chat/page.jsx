'use client';

import React,{useState,useEffect} from 'react';
import { withPageAuthRequired, useUser } from '@auth0/nextjs-auth0/client';
import Highlight from '../../components/Highlight';


export default withPageAuthRequired(function ChatPage() {

   // States for chat creation
   const [name, setName] = useState('');
   const [description, setDescription] = useState('');
   const [invites, setInvites] = useState('');
   const [chats, setChats] = useState([]);
   const [selectedChat, setSelectedChat] = useState(null);
   const [messages, setMessages] = useState([]);
   const [newMessage, setNewMessage] = useState('');
 
   // Fetch chats where the user is a member
   useEffect(() => {
     async function fetchChats() {
       try {
         const response = await fetch('/api/chats');
         const data = await response.json();
         setChats(data);
       } catch (err) {
         console.error('Error fetching chats:', err);
       }
     }
     fetchChats();
   }, []);
 
   // Fetch messages for the selected chat
   useEffect(() => {
     if (selectedChat) {
       async function fetchMessages() {
         try {
           const response = await fetch(`/api/chats/${selectedChat.id}/messages`);
           const data = await response.json();
           setMessages(data);
         } catch (err) {
           console.error('Error fetching messages:', err);
         }
       }
       fetchMessages();
     }
   }, [selectedChat]);

   async function handleDeleteChat(id) {
      try {
        const response = await fetch(`/api/chats/`, {
          method: 'DELETE',
          body: JSON.stringify({ id }),
        });
        if (!response.ok) throw new Error('Failed to delete chat');
        setChats(prevState => prevState.filter((chat) => chat.id !== id));
      } catch (err) {
        console.error('Error deleting chat:', err);
      }
    }
 
   // Handle creating a new chat
   async function handleCreateChat() {
     try {
       const response = await fetch('/api/chats/create', {
         method: 'POST',
         headers: {
           'Content-Type': 'application/json',
         },
         body: JSON.stringify({
           name,
           description,
           invites: [1]
         }),
       });
       if (!response.ok) throw new Error('Failed to create chat');
       const newChat = await response.json();
       setChats([...chats, newChat]);
       setName('');
       setDescription('');
       setInvites('');
     } catch (err) {
       console.error('Error creating chat:', err);
     }
   }
 
   // Handle sending a new message
   async function handleSendMessage() {
     if (!selectedChat) return;
 
     try {
       const response = await fetch(`/api/chats/${selectedChat.id}/messages`, {
         method: 'POST',
         headers: {
           'Content-Type': 'application/json',
         },
         body: JSON.stringify({ content: newMessage, content_type: 'text' }),
       });
       if (!response.ok) throw new Error('Failed to send message');
       const message = await response.json();
       setMessages([...messages, message]);
       setNewMessage('');
     } catch (err) {
       console.error('Error sending message:', err);
     }
   }
 
   return (
     <div>
       <section>
         <h2>Create Chat</h2>
         <input type="text" placeholder="Chat Name" value={name} onChange={(e) => setName(e.target.value)} />
         <input type="text" placeholder="Description" value={description} onChange={(e) => setDescription(e.target.value)} />
         <input type="text" placeholder="Invite IDs (comma-separated)" value={invites} onChange={(e) => setInvites(e.target.value)} />
         <button onClick={handleCreateChat}>Create Chat</button>
       </section>
 
       <section>
         <h2>Your Chats</h2>
         <ul>
           {chats.map((chat) => (
            <div>
             <li key={chat.id} onClick={() => setSelectedChat(chat)}>
               {chat.name}
               
               
             </li>
             <button onClick={async () => handleDeleteChat(chat.id)}>Delete</button>
              </div>
           ))}
         </ul>
       </section>
 
       {selectedChat && (
         <section>
           <h2>Chat: {selectedChat.name}</h2>
           <div>
             {messages && messages?.map((message) => (
               <div key={message.id}>
                 <strong>{message.sender}</strong>: {message.content}
               </div>
             ))}
           </div>
           <input
             type="text"
             placeholder="Type a message..."
             value={newMessage}
             onChange={(e) => setNewMessage(e.target.value)}
           />
           <button onClick={handleSendMessage}>Send</button>
         </section>
       )}
     </div>
   );
});
