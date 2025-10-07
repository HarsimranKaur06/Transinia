// API utility functions for connecting to the backend
import { UploadResponse, Transcript, Insight, ActionItem } from '@/types';

// Use build-time env NEXT_PUBLIC_BACKEND_URL injected during Docker build, fallback to localhost
const API_URL = (process && (process.env as Record<string, string | undefined>)?.NEXT_PUBLIC_BACKEND_URL) || 'http://localhost:8001';
console.log("Using API URL:", API_URL);

/**
 * Upload a transcript file to the backend
 */
export async function uploadTranscript(file: File): Promise<UploadResponse> {
  try {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_URL}/api/transcripts/upload`, {
      method: 'POST',
      body: formData,
    });

    const data = await response.json();
    
    if (!response.ok) {
      throw new Error(data.message || 'Failed to upload transcript');
    }

    return {
      success: true,
      message: 'File uploaded successfully',
      fileId: data.fileId,
    };
  } catch (error) {
    console.error('Error uploading transcript:', error);
    return {
      success: false,
      message: error instanceof Error ? error.message : 'Failed to upload transcript',
    };
  }
}

/**
 * Fetch the list of available transcripts
 */
export async function getTranscripts(): Promise<Transcript[]> {
  try {
    console.log("Attempting to fetch transcripts from:", `${API_URL}/api/transcripts/list`);
    const response = await fetch(`${API_URL}/api/transcripts/list`, {
      method: 'GET',
      mode: 'cors',
      headers: {
        'Accept': 'application/json',
      },
    });
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error("API response not OK:", response.status, errorText);
      throw new Error(`Failed to fetch transcripts: ${response.status} ${errorText}`);
    }

    const data = await response.json();
    console.log("API Response data:", data);
    return data.transcripts || [];
  } catch (error) {
    console.error('Error fetching transcripts:', error);
    return [];
  }
}

/**
 * Generate meeting data from a transcript
 */
export async function generateInsights(transcriptId: string): Promise<{ 
  success: boolean; 
  message: string; 
  meetingDataId?: string;
  alreadyProcessed?: boolean;
}> {
  try {
    const response = await fetch(`${API_URL}/api/meeting-data/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ transcriptId }),
    });

    const data = await response.json();
    
    if (!response.ok) {
      throw new Error(data.message || 'Failed to generate meeting data');
    }

    return {
      success: true,
      message: data.message || 'Meeting data generated successfully',
      meetingDataId: data.meetingDataId,
      alreadyProcessed: data.alreadyProcessed || false
    };
  } catch (error) {
    console.error('Error generating meeting data:', error);
    return {
      success: false,
      message: error instanceof Error ? error.message : 'Failed to generate meeting data',
    };
  }
}

/**
 * Fetch meeting data by ID
 */
export async function getInsight(insightId: string): Promise<{ success: boolean; insight?: Insight; message?: string }> {
  try {
    const response = await fetch(`${API_URL}/api/meeting-data/${insightId}`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch meeting data');
    }

    const data = await response.json();
    
    return {
      success: true,
      insight: data,
    };
  } catch (error) {
    console.error('Error fetching meeting data:', error);
    return {
      success: false,
      message: error instanceof Error ? error.message : 'Failed to fetch meeting data',
    };
  }
}

/**
 * Fetch all meeting data
 */
export async function getMeetings(): Promise<Insight[]> {
  try {
    const response = await fetch(`${API_URL}/api/meeting-data/list`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch meetings');
    }

    const data = await response.json();
    return data.meetingData || [];
  } catch (error) {
    console.error('Error fetching meetings:', error);
    return [];
  }
}

/**
 * Fetch high priority tasks
 */
export async function getHighPriorityTasks(): Promise<ActionItem[]> {
  try {
    const response = await fetch(`${API_URL}/api/tasks/high-priority`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch high priority tasks');
    }

    const data = await response.json();
    return data.tasks || [];
  } catch (error) {
    console.error('Error fetching high priority tasks:', error);
    return [];
  }
}

/**
 * Get original transcript content by ID
 */

/**
 * Update an action item's completion status
 */
export async function updateActionItem(insightId: string, actionItemId: string, completed: boolean): Promise<{ success: boolean; message: string }> {
  try {
    const response = await fetch(`${API_URL}/api/meeting-data/${insightId}/actions/${actionItemId}`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ completed }),
    });

    if (!response.ok) {
      throw new Error('Failed to update action item');
    }

    await response.json(); // We don't use the response data but need to consume it
    return {
      success: true,
      message: 'Action item updated successfully',
    };
  } catch (error) {
    console.error('Error updating action item:', error);
    return {
      success: false,
      message: error instanceof Error ? error.message : 'Failed to update action item',
    };
  }
}
