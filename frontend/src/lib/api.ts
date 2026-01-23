// src/lib/api.ts
// API utility functions for connecting to the backend
import { UploadResponse, Transcript, Insight, ActionItem } from "@/types";

// Prefer NEXT_PUBLIC_API_URL, fall back to NEXT_PUBLIC_BACKEND_URL, then localhost
const API_URL: string =
  (process.env.NEXT_PUBLIC_API_URL as string | undefined) ??
  (process.env.NEXT_PUBLIC_BACKEND_URL as string | undefined) ??
  "http://localhost:8001";

// ----- Types for results where we return a union shape -----

export type GenerateInsightsResult = {
  success: boolean;
  message: string;
  meetingDataId?: string;
  alreadyProcessed?: boolean;
};

export type GetInsightResult =
  | { success: true; insight: Insight }
  | { success: false; message: string };

// ----- Helpers -----

function jsonHeaders(): HeadersInit {
  return { "Content-Type": "application/json", Accept: "application/json" };
}

async function parseJson<T>(res: Response): Promise<T> {
  // Let it throw on invalid JSON to be handled by the caller
  return (await res.json()) as T;
}

function errorMessage(err: unknown, fallback: string): string {
  return err instanceof Error ? err.message : fallback;
}

// ----- API Calls -----

/**
 * Upload a transcript file to the backend
 */
export async function uploadTranscript(file: File): Promise<UploadResponse> {
  try {
    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch(`${API_URL}/api/transcripts/upload`, {
      method: "POST",
      body: formData,
    });

    const data = (await parseJson<{ fileId?: string; message?: string }>(response)) || {};

    if (!response.ok) {
      throw new Error(data.message ?? "Failed to upload transcript");
    }

    return {
      success: true,
      message: "File uploaded successfully",
      fileId: data.fileId,
    };
  } catch (err) {
    return {
      success: false,
      message: errorMessage(err, "Failed to upload transcript"),
    };
  }
}

/**
 * Fetch the list of available transcripts
 */
export async function getTranscripts(): Promise<Transcript[]> {
  try {
    const response = await fetch(`${API_URL}/api/transcripts/list`, {
      method: "GET",
      headers: { Accept: "application/json" },
      cache: "no-store",
    });

    if (!response.ok) {
      const text = await response.text();
      throw new Error(`Failed to fetch transcripts: ${response.status} ${text}`);
    }

    const data = (await parseJson<{ transcripts?: Transcript[] }>(response)) || {};
    return data.transcripts ?? [];
  } catch {
    return [];
  }
}

/**
 * Generate meeting data from a transcript
 */
export async function generateInsights(transcriptId: string): Promise<GenerateInsightsResult> {
  try {
    const response = await fetch(`${API_URL}/api/meeting-data/generate`, {
      method: "POST",
      headers: jsonHeaders(),
      body: JSON.stringify({ transcriptId }),
    });

    const data =
      (await parseJson<{
        message?: string;
        meetingDataId?: string;
        alreadyProcessed?: boolean;
      }>(response)) || {};

    if (!response.ok) {
      throw new Error(data.message ?? "Failed to generate meeting data");
    }

    return {
      success: true,
      message: data.message ?? "Meeting data generated successfully",
      meetingDataId: data.meetingDataId,
      alreadyProcessed: Boolean(data.alreadyProcessed),
    };
  } catch (err) {
    return {
      success: false,
      message: errorMessage(err, "Failed to generate meeting data"),
    };
  }
}

/**
 * Fetch meeting data by ID
 */
export async function getInsight(insightId: string): Promise<GetInsightResult> {
  try {
    const response = await fetch(`${API_URL}/api/meeting-data/${insightId}`, {
      headers: { Accept: "application/json" },
      cache: "no-store",
    });

    if (!response.ok) {
      throw new Error("Failed to fetch meeting data");
    }

    const data = await parseJson<Insight>(response);
    return { success: true, insight: data };
  } catch (err) {
    return { success: false, message: errorMessage(err, "Failed to fetch meeting data") };
  }
}

/**
 * Fetch all meeting data
 */
export async function getMeetings(): Promise<Insight[]> {
  try {
    const response = await fetch(`${API_URL}/api/meeting-data/list`, {
      headers: { Accept: "application/json" },
      cache: "no-store",
    });

    if (!response.ok) {
      throw new Error("Failed to fetch meetings");
    }

    const data = (await parseJson<{ meetingData?: Insight[] }>(response)) || {};
    return data.meetingData ?? [];
  } catch {
    return [];
  }
}

/**
 * Fetch high priority tasks
 */
export async function getHighPriorityTasks(): Promise<ActionItem[]> {
  try {
    const response = await fetch(`${API_URL}/api/tasks/high-priority`, {
      headers: { Accept: "application/json" },
      cache: "no-store",
    });

    if (!response.ok) {
      throw new Error("Failed to fetch high priority tasks");
    }

    const data = (await parseJson<{ tasks?: ActionItem[] }>(response)) || {};
    return data.tasks ?? [];
  } catch {
    return [];
  }
}

/**
 * Update an action item's completion status
 */
export async function updateActionItem(
  insightId: string,
  actionItemId: string,
  completed: boolean,
): Promise<{ success: boolean; message: string }> {
  try {
    const response = await fetch(`${API_URL}/api/meeting-data/${insightId}/actions/${actionItemId}`, {
      method: "PATCH",
      headers: jsonHeaders(),
      body: JSON.stringify({ completed }),
    });

    if (!response.ok) {
      throw new Error("Failed to update action item");
    }

    // Response body is not required by the UI, just ensure it’s consumed.
     
    await response.json();

    return { success: true, message: "Action item updated successfully" };
  } catch (err) {
    return { success: false, message: errorMessage(err, "Failed to update action item") };
  }
}
