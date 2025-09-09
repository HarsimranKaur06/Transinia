# Transinia Frontend Integration

This document explains how to integrate and use the frontend with the Transinia application.

## Overview

The frontend is designed to be completely separate from the backend code, allowing you to:
1. Test and develop the frontend independently
2. Easily remove it if needed without affecting the core application
3. Deploy it separately (e.g., to Vercel) while keeping the backend on your own infrastructure

## Running the Frontend

The frontend is a Next.js application located in the `frontend/` directory:

```bash
# Navigate to the frontend directory
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

Then open [http://localhost:3000](http://localhost:3000) in your browser.

## Connecting to the Backend

By default, the frontend uses mock data for development. To connect it to your actual backend:

1. Ensure your Transinia backend is running (using Docker or directly)
2. Update the `.env.local` file in the frontend directory with your backend URLs:
   ```
   NEXT_PUBLIC_API_URL=http://localhost:8000/api
   NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
   NEXT_PUBLIC_S3_BUCKET_NAME=your-bucket-name
   ```
3. Modify the API service files to use the actual endpoints

## Frontend Features

The frontend includes:

1. **Landing Page**: Introduces the application and its features
2. **Transcripts Page**: Upload new transcripts or select existing ones from S3
3. **Dashboard**: View meeting statistics, recent meetings, and high-priority tasks

## Deployment Options

You can deploy the frontend to Vercel for easy hosting:

1. Push your code to GitHub
2. Connect your repository to Vercel
3. Configure the environment variables in the Vercel dashboard
4. Deploy

## Removing the Frontend

If you decide not to use the frontend, you can easily remove it:

1. Switch back to your main branch: `git checkout dev`
2. Delete the frontend branch: `git branch -D frontend-dev` 
3. Remove the frontend directory: `rm -rf frontend`

This will not affect your backend code in any way.
