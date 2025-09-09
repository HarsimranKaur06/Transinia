# Transinia Frontend

This directory contains a simple frontend for the Transinia application. The frontend is built using Next.js and Tailwind CSS and is completely isolated from the rest of your application.

## Features

- Landing page with project description and features
- Transcript management page for uploading and browsing transcripts
- Dashboard for viewing meeting insights and statistics
- API integration with the existing Transinia backend

## Getting Started

1. Navigate to the frontend directory:
   ```
   cd frontend
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Create a `.env.local` file with the following variables:
   ```
   NEXT_PUBLIC_API_URL=http://localhost:3000/api
   NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
   NEXT_PUBLIC_S3_BUCKET_NAME=transinia-transcripts
   ```

4. Start the development server:
   ```
   npm run dev
   ```

5. Open [http://localhost:3000](http://localhost:3000) in your browser.

## Integration with Backend

The frontend is designed to integrate with your existing Transinia backend. Currently, it uses mock data for development purposes, but it can be connected to the actual backend by updating the API service in `src/lib/api/index.js`.

## Important Notes

- This frontend is on a separate branch (`frontend-dev`) to ensure it doesn't interfere with your existing code.
- No changes have been made to your existing backend code.
- The frontend can be easily removed if needed by deleting the `frontend` directory.

## Removing the Frontend

If you decide you don't want to use the frontend, you can remove it completely:

1. Switch back to your main branch:
   ```
   git checkout dev
   ```

2. Delete the frontend branch:
   ```
   git branch -D frontend-dev
   ```

3. Remove the frontend directory:
   ```
   rm -rf frontend
   ```

These steps will completely remove the frontend without affecting your existing backend code.
