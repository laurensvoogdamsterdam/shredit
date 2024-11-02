// pages/api/files/upload.js
import { getAccessToken, withApiAuthRequired } from '@auth0/nextjs-auth0';
import { url } from 'inspector';
import { NextResponse } from 'next/server';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

// create POST /api/files/upload to get signed url
export const POST = withApiAuthRequired(async function getSignedUrl(req) {
    try {
        const { accessToken } = await getAccessToken(req); 
        const {file_name, content_type, operation} = await req.json(); 
        
        

        const response = await fetch(`${BACKEND_URL}/files/signedurl`, {
            method: 'POST',            
            cache: 'no-store',
            headers: {
                'Content-Type': 'application/json',
                Authorization: `Bearer ${accessToken}`,
            },
            body: JSON.stringify({file_name:file_name, content_type: content_type, operation:'upload'}),
        });

        if (!response.ok) {
            throw new Error(`Failed to get signed URL: ${response.statusText}`);
        }

        const data = await response.json();
        return NextResponse.json(data);
    } catch (error) {
        console.error("Error getting signed URL:", error);
        return NextResponse.json(
            { error: error.message },
            { status: error.status || 500 }
        );
    }
});


export const PUT = withApiAuthRequired(async function uploadFile(req) {
    try {
        const { url } = req.query; // Get presigned URL from query parameters
        const file = req.body; // The file data

        const response = await fetch(url, {
            method: 'PUT',
            body: file,
            headers: {
                'Content-Type': file.type,
            },
        });

        if (!response.ok) {
            throw new Error(`Failed to upload file: ${response.statusText}`);
        }

        return NextResponse.json({ message: 'Upload successful' });
    } catch (error) {
        console.error("Error uploading file:", error);
        return NextResponse.json(
            { error: error.message },
            { status: error.status || 500 }
        );
    }
});


export const GET = withApiAuthRequired(async function listFiles(req) {
    try {
        const { accessToken } = await getAccessToken(req); // Get access token

        const response = await fetch(`${BACKEND_URL}/files`, {
            method: 'GET',
            headers: {
                Authorization: `Bearer ${accessToken}`,
            },
        });

        if (!response.ok) {
            throw new Error(`Failed to list files: ${response.statusText}`);
        }

        const data = await response.json();
        return NextResponse.json(data);
    } catch (error) {
        console.error("Error listing files:", error);
        return NextResponse.json(
            { error: error.message },
            { status: error.status || 500 }
        );
    }
});


export const DELETE = withApiAuthRequired(async function deleteFile(req) {
    try {
        const { fileId } = await req.json(); // Get file ID from request body
        const { accessToken } = await getAccessToken(req); // Get access token
        console.log(fileId)

        const response = await fetch(`${BACKEND_URL}/files/${fileId}`, {
            method: 'DELETE',
            headers: {
                Authorization: `Bearer ${accessToken}`,
            },
        });

        if (!response.ok) {
            throw new Error(`Failed to delete file: ${response.statusText}`);
        }

        return NextResponse.json({ message: 'File deleted successfully' });
    } catch (error) {
        console.error("Error deleting file:", error);
        return NextResponse.json(
            { error: error.message },
            { status: error.status || 500 }
        );
    }
});

