# Frontend Dockerfile

This folder contains the Next.js frontend and a production multi-stage `Dockerfile`.

# Build (pass backend URL as build-arg so Next.js bakes NEXT_PUBLIC_BACKEND_URL into the build):

```
docker build -t transinia-frontend:latest \
  --build-arg NEXT_PUBLIC_BACKEND_URL="http://backend:8001" \
  -f frontend/Dockerfile frontend
```

Run (map port 3000):

```
docker run --rm -p 3000:3000 transinia-frontend:latest
```

Notes:
- NEXT_PUBLIC_* env vars are baked into the build by Next.js. To change them you must rebuild the image with new build-args.
- For local development use `npm run dev` instead of the Docker image.
# Transinia Frontend

This is the frontend for Transinia, a tool for analyzing meeting transcripts using AI.

## Overview

The Transinia frontend provides a user interface for:

1. Uploading transcripts to be processed
2. Browsing existing transcripts in S3
3. Viewing meeting minutes, action items, and decisions
4. Searching for meetings by participant
5. Tracking tasks and their status

## Getting Started

First, install dependencies and run the development server:

```bash
cd frontend
npm install
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

## Environment Variables

Create a `.env.local` in the `frontend/` directory with:

```
NEXT_PUBLIC_API_URL=http://localhost:3000/api   # if using Next proxy
NEXT_PUBLIC_BACKEND_URL=http://localhost:5000   # direct calls to backend
NEXT_PUBLIC_S3_BUCKET_NAME=your-bucket-name
```

Adjust ports/URLs to match your backend configuration (e.g. App Runner or ECS URL in production).

## Features

- **Upload Transcripts**: Easily upload meeting transcript files (.txt, .docx, .md)
- **Generate Insights**: Process transcripts to extract key information using AI
- **View Summaries**: See meeting summaries, action items, and key points
- **Track Tasks**: Monitor action items and mark them as complete
- **Participant Information**: View who attended meetings and their responsibilities

## Project Structure

```
frontend/
├── src/
│   ├── app/
│   │   ├── dashboard/            # Dashboard page
│   │   ├── transcripts/          # Transcript management page
│   │   ├── insights/[id]/        # Dynamic insights page
│   │   ├── layout.tsx            # Root layout
│   │   └── page.tsx              # Landing page
│   ├── lib/
│   │   ├── api.ts                # API integration with backend
│   │   └── utils.ts              # Utility functions
│   ├── types/
│   │   └── index.ts              # Type definitions
│   └── components/               # Reusable UI components
├── public/                       # Static assets
└── .env.local                    # Environment variables
```

## Integration with Backend

The frontend connects to the Transinia backend via API calls defined in `src/lib/api.ts`. 

To connect to the actual backend:

1. Ensure the backend is running (e.g., `python run_api.py` or running container on port 5000)
2. Update `.env.local` with the correct URLs (see **Environment Variables** above)
3. Restart the frontend dev server

The application uses a proxy or direct URLs to handle CORS issues.

## Technologies Used

- **Next.js 15+**: React framework with server-side rendering
- **TypeScript**: Type-safe JavaScript
- **Tailwind CSS**: Utility-first CSS framework
- **Lucide Icons**: Simple and consistent icon set

## Deployment Options

### Deploy on Vercel (Quickest)

1. Push your code to GitHub
2. Connect your repository to [Vercel](https://vercel.com/new)
3. Configure the environment variables (`NEXT_PUBLIC_BACKEND_URL`, etc.) in the Vercel dashboard
4. Deploy — Vercel will auto-build and give you a live URL

### Deploy on AWS Amplify

1. Go to AWS Amplify → New App → Host web app
2. Select your GitHub repo and choose the `frontend/` folder
3. Configure env vars (same as `.env.local`)
4. Deploy — Amplify will build and provide a CDN-backed HTTPS URL

## Clean Uninstallation

To remove the frontend while keeping the backend:

```bash
rm -rf frontend
```

This will not affect your backend code.

## Notes

- The frontend is designed to be **completely separate** from the backend, so you can run and deploy them independently.
- In production, point `NEXT_PUBLIC_BACKEND_URL` to your deployed backend URL (e.g., App Runner or ECS service).

