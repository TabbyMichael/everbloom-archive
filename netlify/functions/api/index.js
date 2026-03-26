// Netlify Function for API Proxy
const fetch = require('node-fetch');

exports.handler = async (event, context) => {
  const { path, httpMethod, headers, body } = event;
  
  // Backend API URL - replace with your deployed backend
  const BACKEND_URL = 'https://your-backend-url.com';
  
  try {
    const response = await fetch(`${BACKEND_URL}${path}`, {
      method: httpMethod,
      headers: {
        'Content-Type': 'application/json',
        ...headers,
      },
      body: body ? JSON.parse(body) : undefined,
    });

    const data = await response.text();
    
    return {
      statusCode: response.status,
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        'Content-Type': response.headers.get('content-type') || 'application/json',
      },
      body: data,
    };
  } catch (error) {
    return {
      statusCode: 500,
      body: JSON.stringify({ error: 'Internal Server Error' }),
    };
  }
};
