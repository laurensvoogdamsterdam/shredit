'use client';

import React,{useState,useEffect} from 'react';
import { withPageAuthRequired, useUser } from '@auth0/nextjs-auth0/client';
import Highlight from '../../components/Highlight';


export default withPageAuthRequired(function CSRPage() {
    const [files, setFiles] = useState([]);
    const [file, setFile] = useState(null);
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        fetchFiles();
    }, []);

    const fetchFiles = async () => {
        setLoading(true);
        setError(null);

        try {
            const response = await fetch('/api/files');
            if (!response.ok) throw new Error('Failed to fetch files');
            const data = await response.json();
            setFiles(data);
        } catch (error) {
            setError(error.message);
        } finally {
            setLoading(false);
        }
    };

    const handleFileChange = (e) => {
        setFile(e.target.files[0]);
    };

    const handleUpload = async () => {
        if (!file) return;

        try {
            // get file_name and content_type from file 
            const { name, type } = file;
            

            // Fetch the presigned URL from the backend
            const response = await fetch(`/api/files`, {
                method: 'POST',
                body: JSON.stringify({ file_name: name, content_type: type, operation: 'upload' }), 
            });

            var { signed_url } = await response.json();
            console.log(signed_url)
            

            // Upload the file to the presigned URL
            const uploadResponse = await fetch(signed_url, {
                method: 'PUT',
                body: file,
                headers: {
                    'Content-Type': type, // Set content type from the file object
                },
            });


            if (!uploadResponse.ok) throw new Error('Failed to upload file');
            fetchFiles(); // Refresh the file list after successful upload
        } catch (error) {
            setError(error.message);
        }
    };

    const handleDelete = async (fileId) => {
        // if (!confirm('Are you sure you want to delete this file?')) return;

        try {
            const response = await fetch(`/api/files?fileId=${fileId}`, {
                method: 'DELETE',
                body: JSON.stringify({ fileId }), // Send the file ID in the request body 
            });
            if (!response.ok) throw new Error('Failed to delete file');
            // fetchFiles(); // Refresh the file list after successful deletion
            setFiles((prevFiles) => prevFiles.filter((file) => file.id !== fileId));
        } catch (error) {
          console.log(error)
            setError(error.message);
        }
    };

    return (
        <div>
            <h1>File Storage</h1>

            {error && <p style={{ color: 'red' }}>Error: {error}</p>}

            <input type="file" onChange={handleFileChange} />
            <button onClick={handleUpload} disabled={!file || loading}>
                Upload
            </button>

            {loading ? (
                <p>Loading files...</p>
            ) : (
                <ul>
                    {files.map((file) => (
                        <li key={file.id}>
                            {/* check in content_type is image */}
                            {file.content_type.startsWith('image/') ? (
                                <img src={file.file_url} alt={file.file_name} style={{ width: 100 }} />
                            ) : (
                            <a href={file.file_url} target="_blank" rel="noopener noreferrer">
                                  find file: {file.file_url}
                            </a>
                            )}
                            {/* check if file is csv */}
                            <button onClick={() => handleDelete(file.id)}>Delete</button>
                        </li>
                    ))}
                </ul>
            )}
        </div>
    );
});
