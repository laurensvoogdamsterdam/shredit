'use client';

import React from 'react';
import { withPageAuthRequired, useUser } from '@auth0/nextjs-auth0/client';
import Highlight from '../../components/Highlight';


export default withPageAuthRequired(function CSRPage() {

  //  get accessToken for the user for the API
  

  const [shows, setShows] = React.useState([]);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState(null);
  const [query, setQuery] = React.useState('');

  // fetch /api/shows
  React.useEffect(() => {
    // Fetch the data inside useEffect
    const fetchShows = async () => {
      try {

        const response = await fetch(`http://localhost:3000/api/shows?q=${query}`); 
       
        if (!response.ok) {
          throw new Error(`Error: ${response.statusText}`);
        }
        const data = await response.json();
        setShows(data); // Update state with the fetched data
      } catch (err) {
        console.error(err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchShows(); // Call the async function
  }, [query]); 


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
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search for shows"
            />
          </p>
          {/* put shows in coe snippet */}
          

        </div>
      </div>
    </>
  );
});
