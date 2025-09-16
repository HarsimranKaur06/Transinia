// Global type definitions for the application

// Transcript type
export interface Transcript {
  id: string;
  name: string;
  date: string;
  processed: boolean;
  meetingDataId?: string;
  size?: number;
  source?: string;
}

// Action Item type (for meeting insights)
export interface ActionItem {
  id: string;
  text: string;
  assignee?: string;
  completed: boolean;
  priority?: string;
}

// Meeting Insight type
export interface Insight {
  id: string;
  title: string;
  date: string;
  summary: string;
  executiveSummary?: string;
  actionItems: ActionItem[];
  keyPoints: string[];
  participants: string[];
  duration: string;
  source?: string;
  // Add more fields as needed for your application
}

// API response types
export interface ApiResponse<T> {
  success: boolean;
  message?: string;
  data?: T;
}

export interface UploadResponse {
  success: boolean;
  message: string;
  fileId?: string;
}

export interface TranscriptsResponse {
  success: boolean;
  transcripts: Transcript[];
}

export interface InsightResponse {
  success: boolean;
  message: string;
  insight?: Insight;
}
