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
        <h1 data-testid="csr-title">Client-side Rendered Page</h1>
        <div data-testid="csr-text">
          <p>
            You can protect a client-side rendered page by wrapping it with <code>withPageAuthRequired</code>. Only
            logged in users will be able to access it. If the user is logged out, they will be redirected to the login
            page instead.
          </p>
          <p>
            Use the <code>useUser</code> hook to access the user profile from protected client-side rendered pages. The{' '}
            <code>useUser</code> hook relies on the <code>UserProvider</code> Context Provider, so you need to wrap your
            custom <a href="https://nextjs.org/docs/advanced-features/custom-app">App Component</a> with it.
          </p>
          <p>
            You can also fetch the user profile by calling the <code>/api/auth/me</code> API route.
          </p>
          <p>
            The following data is fetched from the <code>/api/shows</code> API route.
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search for shows"
            />
          </p>
          {/* put shows in coe snippet */}
          <pre>
            <Highlight>{JSON.stringify(shows, null, 2)}</Highlight> 
          </pre>

        </div>
      </div>
    </>
  );
});
