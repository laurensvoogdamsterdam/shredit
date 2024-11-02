import { getAccessToken, withApiAuthRequired } from '@auth0/nextjs-auth0';
import { NextResponse } from 'next/server';

export const POST = withApiAuthRequired(async function sendMessage(req, { params }) {
  try {
    console.log(params)
    const { id } = params
    const { content,content_type } = await req.json();
    const { accessToken } = await getAccessToken(req);
    console.log('id',id)
    console.log('message',content)
    console.log('content_type',content_type)


    const response = await fetch(`http://localhost:8000/chats/${id}/messages`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${accessToken}`,
      },
      body: JSON.stringify({ content: content,content_type:'text' }),
    });

    if (!response.ok) {
      throw new Error(`Failed to create chat: ${response.statusText}`);
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error("Error creating chat:", error);
    return NextResponse.json(
      { error: error.message },
      { status: error.status || 500 }
    );
  }
});

export const GET = withApiAuthRequired(async function getMessages(req, { params }) {
  try {
    // read id from [id] param
    const { id } = params;  
    //  get accessToken
    const { accessToken } = await getAccessToken(req);
    // send gET to http://localhost:8000/chats/${id}/messages

    const response = await fetch(`http://localhost:8000/chats/${id}/messages`, {
      method: 'GET',
      headers: {
        Authorization: `Bearer ${accessToken}`
      },
    });
    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error("Error creating chat:", error);
   return NextResponse.json([]);
  }
});
