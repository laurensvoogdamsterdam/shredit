'use client';

import React, {useState,useEffect} from 'react';
import { withPageAuthRequired, useUser } from '@auth0/nextjs-auth0/client';
import Highlight from '../../components/Highlight';


export default withPageAuthRequired(function WorkflowPage() {

  const [workflowId, setWorkflowId] = useState(null);
  const [status, setStatus] = useState(null);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [workflows, setWorkflows] = useState([]);
  const [instances, setInstances] = useState([]); 

  // start instance with workflow id
  const startInstance = async (workflowId) => {
    setError(null);
    try {
      const response = await fetch('http://localhost:3000/api/workflows', {
        method: 'POST',        
        body: JSON.stringify({ id:workflowId }),
      });

      if (!response.ok) {
        throw new Error(`Failed to start instance: ${response.statusText}`);
      }

      const data = await response.json();
      setInstances([...instances, data]); // Add the new instance to the list
    } catch (err) {
      console.error(err);
      setError(err.message);
    }
  };

  async function getWorkflowInstances() { 
    try {
      const response = await fetch('http://localhost:3000/api/workflows/instance');
      const data = await response.json();
      setInstances(data);
    } catch (err) {
      console.error('Error fetching instances:', err);
    }
  }


  

  // Start workflow and retrieve a workflow ID
  const startWorkflow = async () => {
    setError(null);
    try {
      const { accessToken } = await getAccessToken();
      const response = await fetch('http://localhost:3000/api/workflows/start', {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to start workflow: ${response.statusText}`);
      }

      const data = await response.json();
      setWorkflowId(data.workflowId); // Set the workflow ID returned from the server
      setStatus('Running');
    } catch (err) {
      console.error(err);
      setError(err.message);
    }
  };

  useEffect(() => {
    // fetch workflows
    const fetchWorkflows = async () => {
      const response = await fetch('http://localhost:3000/api/workflows', {});

      if (!response.ok) {
        throw new Error(`Failed to fetch workflows: ${response.statusText}`);
      }

      const data = await response.json();
      setWorkflows(data);
    };

    fetchWorkflows();
    getWorkflowInstances();
  }
  , []);

  // Polling function to check workflow status
  useEffect(() => {
    if (!workflowId || status === 'Completed' || status === 'Failed') return;

    const checkStatus = async () => {
      try {
        const { accessToken } = await getAccessToken();
        const response = await fetch(`http://localhost:3000/api/workflows/status?workflowId=${workflowId}`, {
          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
        });

        if (!response.ok) {
          throw new Error(`Failed to fetch workflow status: ${response.statusText}`);
        }

        const data = await response.json();
        setStatus(data.status);

        if (data.status === 'Completed') {
          setResults(data.results); // Retrieve results if completed
        }
      } catch (err) {
        console.error(err);
        setError(err.message);
      }
    };

    const intervalId = setInterval(checkStatus, 3000); // Poll every 3 seconds
    return () => clearInterval(intervalId);
  }, [workflowId, status]);

  return (
    <div>
      <h1>Trigger and Track Workflow</h1>

      <button onClick={startWorkflow} disabled={status === 'Running'}>
        Start Workflow
      </button>

      {/*  if workflows map over them */}
      <ul>
        {workflows.map((workflow) => (
          <li key={workflow.id}>
            <p>{workflow.name} {workflow.id}</p>
            <button onClick={() => startInstance(workflow.id)}>Start</button>
            
          </li>
        ))}
      </ul>

      {error && <p style={{ color: 'red' }}>Error: {error}</p>}

      {workflowId && (
        <>
          <p>Workflow ID: {workflowId}</p>
          <p>Status: {status}</p>
        </>
      )}

      {/* loop over instances */}
      <ul>
        {instances.map((instance) => (
          <li key={instance.id}>
            <p>{instance.id}</p>
            <p>{instance.workflow_id}</p>
            <p>{instance.container_id}</p>
            <p>{instance.status}</p>
          </li>
        ))}
      </ul>

      {status === 'Completed' && (
        <div>
          <h2>Workflow Results</h2>
          <pre>
            <Highlight>{JSON.stringify(results, null, 2)}</Highlight>
          </pre>
        </div>
      )}
    </div>
  );
});
