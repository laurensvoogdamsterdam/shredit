'use client';

import React from 'react';
import { withPageAuthRequired, useUser } from '@auth0/nextjs-auth0/client';
import Highlight from '../../components/Highlight';


export default withPageAuthRequired(function CSRPage() {

  //  get accessToken for the user for the API
  

  const [conversation, setConversation] = React.useState(-1);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState(null);
  const [query, setQuery] = React.useState('');
  const [history, setHistory] = React.useState([]);
  const [answer, setAnswer] = React.useState('');

  
  // create conversation
  async function createConversation() {
    try {
      const res = await fetch(`/api/llm`,{
        method: 'POST',
        cache: 'no-store',
        headers: {
          'Content-Type': 'application/json',
        },        
      })
      if (!res.ok) {
        throw new Error(res.statusText);
      }
      const data = await res.json();
      setConversation(data.id);
    } catch (error) {
      setError(error);
    } finally {
      setLoading(false);
    }
  }

  async function handleChat() {
    try {
      const res = await fetch(`/api/llm/${conversation}`,{
        method: 'POST',
        cache: 'no-store',
        headers: {
          'Content-Type': 'application/json',
        },        
        body: JSON.stringify({content:query, role:'user'})
      })
      if (!res.ok) {
        throw new Error(res.statusText);
      }
      const data = await res.json();
      setHistory(prevState => [...prevState, {role: 'user', content: query}]);
      setHistory(prevState => [...prevState, {role: 'agent', content: data.content}]);

    } catch (error) {
      setError(error);
    } finally {
      setLoading(false);
    }
  }


  return (
    <>
      <div className="mb-5" data-testid="csr">
        <h1 data-testid="csr-title">Large Language Models </h1>
        <div data-testid="csr-text">
          <p>
            This page is an overview of the LLM capabilities of this app.
            You can chat with a different set of persona and do different types of tool calls/function calls, to extend on the context of the LLM
          </p>
          
          <p>
            Chat with a persona
          </p>
          <p>
            The following data is fetched from the <code>/api/shows</code> API route.
            {`
            `}
            
             {conversation < 0 ? (
              <button onClick={async ()=> await  createConversation()}>Create Conversation</button>
             ) : (
              <Highlight>LLM Chat {conversation}</Highlight>
              )}


            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search for shows"
            />
          </p>
          {/* map over history */}
          {history && history.map((item, index) => (
            <div key={index}>
              <p>{item.role}: {item.content}</p>
            </div>
          ))}

          {/* put shows in coe snippet */}
          <button onClick={async ()=> await  handleChat()}>Ask LLM</button>
          

        </div>
      </div>
    </>
  );
});
