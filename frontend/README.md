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

First, run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

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

1. Ensure the backend is running (using `python run_api.py` in the root directory)
2. Update the `.env.local` file with the correct API URL:

```
NEXT_PUBLIC_API_URL=http://localhost:5000
```

3. The application uses a proxy to handle CORS issues with the backend API.

## Technologies Used

- **Next.js 15+**: React framework with server-side rendering
- **TypeScript**: Type-safe JavaScript
- **Tailwind CSS**: Utility-first CSS framework
- **Lucide Icons**: Simple and consistent icon set

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new) from the creators of Next.js.

## Clean Uninstallation

To remove the frontend while keeping the rest of your application intact:

1. Delete the frontend directory:
   ```
   rm -rf frontend
   ```

The frontend is completely isolated from the rest of your application, so removing it will not affect your existing backend code.
