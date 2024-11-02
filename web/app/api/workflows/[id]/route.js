import { getAccessToken, withApiAuthRequired } from '@auth0/nextjs-auth0';
import { NextResponse } from 'next/server';

export const POST = withApiAuthRequired(async function createChat(req) {
  try {
    const { message } = await req.json();
    const { accessToken } = await getAccessToken(req);

    const response = await fetch(`http://localhost:8000/chats/${id}/message`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${accessToken}`,
      },
      body: JSON.stringify({ message: message }),
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
