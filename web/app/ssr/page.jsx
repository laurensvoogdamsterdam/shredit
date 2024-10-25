import React from 'react';
import { getSession, getAccessToken, withPageAuthRequired } from '@auth0/nextjs-auth0';

import Highlight from '../../components/Highlight';

export default withPageAuthRequired(
  async function SSRPage() {
    const { user } = await getSession();
    //  get accessToken for the user for the API
    // get JWT accessToken for API
    const { accessToken } = await getAccessToken();

    // get id token

    // const data = await fetch('http://localhost:8000/users/all', {
    //   headers: {
    //     Authorization: `Bearer ${accessToken}`,
    //   },
    // }).then((res) => res.json());

    // fetch /api/shows
    const response = await fetch('http://localhost:3000/api/shows');
    
    return (
      <>
        <div className="mb-5" data-testid="ssr">
          <h1 data-testid="ssr-title">Server-side Rendered Page</h1>
          <div data-testid="ssr-text">
            <p>
              You can protect a server-side rendered page by wrapping it with <code>withPageAuthRequired</code>. Only
              logged in users will be able to access it. If the user is logged out, they will be redirected to the login
              page instead.{' '}
            </p>
          </div>
        </div>
        <div className="result-block-container" data-testid="ssr-json">
          <div className="result-block">
            <h6 className="muted">User</h6>
            <Highlight>{JSON.stringify(user, null, 2)}</Highlight>
          </div>
        </div>
      </>
    );
  },
  { returnTo: '/ssr' }
);
