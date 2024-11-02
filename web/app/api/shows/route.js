import { getAccessToken, getAccessTokenSilently, withApiAuthRequired } from '@auth0/nextjs-auth0';
import { NextResponse } from 'next/server';

export const GET = withApiAuthRequired(async function shows(req) {
  try {
    const res = new NextResponse();
    // readey query from get params
    const q = req.nextUrl.searchParams.get('q'); 
    const {accessToken} = await getAccessToken(req, res);
    
    const response = await fetch(`http://localhost:8000/users/search?query=${q}`, {
      method: 'GET',
      cache: 'no-store',
      headers: {
        Authorization: `Bearer ${accessToken}`
      },
      
    });
    const data = await response.json();

    return NextResponse.json(data, res);
  } catch (error) {
    console.log(error);
    return NextResponse.json({ error: error.message }, { status: error.status || 500 });
  }
});
