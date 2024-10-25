import { getAccessToken, getAccessTokenSilently, withApiAuthRequired } from '@auth0/nextjs-auth0';
import { NextResponse } from 'next/server';

export const GET = withApiAuthRequired(async function shows(req) {
  try {
    const res = new NextResponse();
    const {accessToken} = await getAccessToken(req, res);
    
    const response = await fetch(`http://localhost:8000/users/me`, {
      // no cache
      cache: 'no-store',
      headers: {
        Authorization: `Bearer ${accessToken}`
      }
    });
    console.log(response)
    const data = await response.json();

    return NextResponse.json(data, res);
  } catch (error) {
    console.log(error);
    return NextResponse.json({ error: error.message }, { status: error.status || 500 });
  }
});
