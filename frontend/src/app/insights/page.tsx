"use client";

import { useRouter } from 'next/navigation';
import { useEffect } from 'react';

export default function InsightsPage() {
  const router = useRouter();

  // Redirect to the transcripts page by default
  useEffect(() => {
    router.push('/transcripts');
  }, [router]);

  return null; // This page doesn't render anything
}
