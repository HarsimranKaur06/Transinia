"use client";

import Link from 'next/link';
import { ArrowLeft, FileText, Upload, Play, Check, RefreshCw, AlertCircle } from 'lucide-react';
import { useState, useEffect } from 'react';
import { uploadTranscript, getTranscripts, generateInsights } from '@/lib/api';
import { useRouter } from 'next/navigation';

// Define TypeScript interfaces for our data
interface Transcript {
  id: string;
  name: string;
  date: string;
  processed: boolean;
  meetingDataId?: string;
}

export default function TranscriptsPage() {
  const router = useRouter();
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [selectedTranscript, setSelectedTranscript] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [processingComplete, setProcessingComplete] = useState(false);
  const [transcripts, setTranscripts] = useState<Transcript[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');

  // Fetch transcripts on component mount
  useEffect(() => {
    async function loadTranscripts() {
      try {
        setIsLoading(true);
        // Try to get real transcripts from the API
        try {
          console.log("Attempting to fetch transcripts from API");
          const apiTranscripts = await getTranscripts();
          console.log("API returned:", apiTranscripts);
          if (apiTranscripts && apiTranscripts.length > 0) {
            setTranscripts(apiTranscripts);
          } else {
            console.log("API returned empty transcripts list");
            // Empty state - no transcripts yet
            setTranscripts([]);
          }
        } catch (e) {
          console.error("Error fetching from API:", e);
          setError('Failed to load transcripts. API connection error.');
          // Don't use sample data for production
          setTranscripts([]);
        }
      } catch (err) {
        setError('Failed to load transcripts. Please try again.');
        console.error('Error loading transcripts:', err);
      } finally {
        setIsLoading(false);
      }
    }

    loadTranscripts();
  }, []);

  const handleFileSelection = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) return;
    
    setIsUploading(true);
    setError(null);
    
    try {
      console.log("Uploading transcript file:", selectedFile.name);
      const result = await uploadTranscript(selectedFile);
      
      if (result.success) {
        console.log("Upload successful");
        // Refresh transcript list
        const updatedTranscripts = await getTranscripts();
        setTranscripts(updatedTranscripts);
        
        // Reset selected file
        setSelectedFile(null);
      } else {
        console.error("Upload failed:", result.message);
        throw new Error(result.message || 'Upload failed');
      }
    } catch (err) {
      setError('Failed to upload file. Please try again.');
      console.error('Error uploading file:', err);
    } finally {
      setIsUploading(false);
    }
  };

  const handleGenerateInsights = async () => {
    if (!selectedTranscript) {
      setError('Please select a transcript first');
      return;
    }
    
    // Check if the transcript has already been processed
    const selectedTranscriptObj = transcripts.find(t => t.id === selectedTranscript);
    if (selectedTranscriptObj?.processed && selectedTranscriptObj?.meetingDataId) {
      // If already processed, redirect directly to the insights page
      router.push(`/insights/${selectedTranscriptObj.meetingDataId}`);
      return;
    }
    
    setIsProcessing(true);
    setProcessingComplete(false);
    setError(null);
    
    try {
      console.log("Generating insights for transcript ID:", selectedTranscript);
      const result = await generateInsights(selectedTranscript);
      
      if (result.success && result.meetingDataId) {
        if (result.alreadyProcessed) {
          console.log("Transcript was already processed. Redirecting to existing insights.");
        } else {
          console.log("Successfully generated new meeting data with ID:", result.meetingDataId);
        }
        
        setProcessingComplete(true);
        
        // Redirect to insights page after a short delay
        setTimeout(() => {
          router.push(`/insights/${result.meetingDataId}`);
        }, 1000);
        
        // Update the transcripts list to reflect the processed status
        setTranscripts(prevTranscripts => 
          prevTranscripts.map(t => 
            t.id === selectedTranscript 
              ? {...t, processed: true, meetingDataId: result.meetingDataId} 
              : t
          )
        );
      } else {
        console.error("Failed to generate insights:", result.message);
        throw new Error(result.message || 'Failed to generate insights');
      }
    } catch (err) {
      setError('Failed to generate insights. Please try again.');
      console.error('Error generating insights:', err);
    } finally {
      setIsProcessing(false);
    }
  };

  // Filter transcripts based on search query
  const filteredTranscripts = transcripts.filter(transcript => 
    transcript.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="flex flex-col min-h-screen">
      {/* Navigation */}
      <header className="border-b">
        <div className="container mx-auto flex h-16 items-center justify-between px-4">
          <div className="flex items-center gap-2">
            <Link href="/" className="text-2xl font-bold">Transinia</Link>
          </div>
          <nav className="ml-auto flex gap-4 sm:gap-6">
            <Link 
              href="/transcripts" 
              className="text-sm font-medium underline underline-offset-4 font-semibold"
            >
              Transcripts
            </Link>
          </nav>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <Link href="/" className="inline-flex items-center text-sm text-neutral-500 hover:text-neutral-900">
            <ArrowLeft className="mr-1 h-4 w-4" />
            Back to Home
          </Link>
          <h1 className="text-3xl font-bold mt-4">Transcript Management</h1>
          <p className="text-neutral-500 mt-2">Upload a new transcript or browse existing ones</p>
          
          <div className="mt-4 bg-blue-50 border border-blue-200 text-blue-700 p-4 rounded-md">
            <h3 className="font-medium">How it works:</h3>
            <ul className="list-disc ml-5 mt-2 text-sm">
              <li>Upload new transcript files using the form on the left</li>
              <li>Select any transcript from the list to work with it</li>
              <li>For <strong>new transcripts</strong>, you'll see a "Generate Meeting Insights" button</li>
              <li>For <strong>already processed transcripts</strong>, you'll see a "View Existing Insights" button</li>
              <li>Processed transcripts are marked with a green badge</li>
            </ul>
          </div>
        </div>

        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md flex items-center">
            <AlertCircle className="h-5 w-5 mr-2" />
            <p>{error}</p>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Upload Section */}
          <div className="bg-white p-6 rounded-lg border">
            <h2 className="text-xl font-semibold mb-4">Upload New Transcript</h2>
            <div className="border-2 border-dashed border-neutral-200 rounded-lg p-8 text-center">
              <div className="flex flex-col items-center">
                <Upload className="h-10 w-10 text-neutral-400 mb-4" />
                <p className="text-neutral-600 mb-2">
                  {selectedFile ? `Selected: ${selectedFile.name}` : 'Drag and drop your transcript file here'}
                </p>
                <p className="text-neutral-400 text-sm mb-4">or</p>
                <input
                  type="file"
                  id="transcript-upload"
                  className="hidden"
                  accept=".txt,.docx,.md"
                  onChange={handleFileSelection}
                />
                <label 
                  htmlFor="transcript-upload"
                  className="inline-flex h-10 items-center justify-center rounded-md bg-neutral-900 px-8 text-sm font-medium text-neutral-50 shadow transition-colors hover:bg-neutral-900/90 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-neutral-950 cursor-pointer"
                >
                  Browse Files
                </label>
                {selectedFile && (
                  <button 
                    onClick={handleUpload}
                    disabled={isUploading}
                    className="mt-4 inline-flex h-10 items-center justify-center rounded-md bg-neutral-900 px-8 text-sm font-medium text-neutral-50 shadow transition-colors hover:bg-neutral-900/90 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-neutral-950 disabled:opacity-50"
                  >
                    {isUploading ? (
                      <><RefreshCw className="mr-2 h-4 w-4 animate-spin" /> Uploading...</>
                    ) : 'Upload File'}
                  </button>
                )}
                <p className="text-xs text-neutral-400 mt-4">Supported formats: .txt, .docx, .md</p>
              </div>
            </div>
          </div>

          {/* Browse Section */}
          <div className="bg-white p-6 rounded-lg border">
            <h2 className="text-xl font-semibold mb-4">Browse Existing Transcripts</h2>
            <div className="border rounded-lg overflow-hidden">
              <div className="bg-neutral-50 py-3 px-4 border-b">
                <input
                  type="text"
                  placeholder="Search transcripts..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full border rounded-md py-2 px-3 text-sm focus:outline-none focus:ring-2 focus:ring-neutral-300"
                />
              </div>
              <div className="divide-y">
                {isLoading ? (
                  <div className="p-8 text-center">
                    <RefreshCw className="h-6 w-6 text-neutral-400 animate-spin mx-auto mb-2" />
                    <p className="text-neutral-500">Loading transcripts...</p>
                  </div>
                ) : filteredTranscripts.length === 0 ? (
                  <div className="p-8 text-center">
                    <FileText className="h-6 w-6 text-neutral-400 mx-auto mb-2" />
                    <p className="text-neutral-500">No transcripts found</p>
                    {searchQuery && (
                      <p className="text-sm text-neutral-400 mt-1">Try a different search term</p>
                    )}
                  </div>
                ) : (
                  /* Map through transcripts */
                  filteredTranscripts.map((transcript) => (
                    <div key={transcript.id} className="p-4 hover:bg-neutral-50 transition-colors cursor-pointer">
                      <div className="flex items-start">
                        <FileText className="h-5 w-5 text-neutral-400 mt-1 mr-3 flex-shrink-0" />
                        <div>
                          <p className="font-medium">
                            {transcript.name}
                            {transcript.processed && (
                              <span className="ml-2 text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded-md inline-block">
                                Processed
                              </span>
                            )}
                          </p>
                          <p className="text-sm text-neutral-500">{transcript.date}</p>
                        </div>
                        <div className="ml-auto flex gap-2">
                          <button 
                            className={`${
                              selectedTranscript === transcript.id 
                                ? "bg-green-100 text-green-700" 
                                : "bg-neutral-100 hover:bg-neutral-200 text-neutral-700"
                            } text-xs px-3 py-1 rounded-md transition-colors`}
                            onClick={() => setSelectedTranscript(transcript.id)}
                          >
                            {selectedTranscript === transcript.id ? (
                              <><Check className="h-3 w-3 inline mr-1" /> Selected</>
                            ) : 'Select'}
                          </button>
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Action area - Show different options based on transcript processed status */}
        <div className="mt-8 flex justify-center">
          {selectedTranscript && (
            <>
              {/* Show View Insights button for processed transcripts */}
              {transcripts.find(t => t.id === selectedTranscript)?.processed ? (
                <Link 
                  href={`/insights/${transcripts.find(t => t.id === selectedTranscript)?.meetingDataId}`}
                  className="inline-flex h-12 items-center justify-center rounded-md px-8 text-sm font-medium shadow transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-neutral-950 bg-blue-600 text-white hover:bg-blue-700"
                >
                  <FileText className="mr-2 h-5 w-5" />
                  View Existing Insights
                </Link>
              ) : (
                /* Show Generate Insights button for unprocessed transcripts */
                <button
                  onClick={handleGenerateInsights}
                  disabled={isProcessing}
                  className={`inline-flex h-12 items-center justify-center rounded-md px-8 text-sm font-medium shadow transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-neutral-950 disabled:opacity-50 ${
                    processingComplete
                      ? "bg-green-600 text-white hover:bg-green-700"
                      : "bg-neutral-900 text-neutral-50 hover:bg-neutral-900/90"
                  }`}
                >
                  {isProcessing ? (
                    <><RefreshCw className="mr-2 h-5 w-5 animate-spin" /> Processing...</>
                  ) : processingComplete ? (
                    <>
                      <Check className="mr-2 h-5 w-5" />
                      Processing Complete
                    </>
                  ) : (
                    <>
                      <Play className="mr-2 h-5 w-5" />
                      Generate Meeting Insights
                    </>
                  )}
                </button>
              )}
            </>
          )}
        </div>
      </div>

      {/* Footer */}
      <footer className="border-t py-6 md:py-8 mt-auto">
        <div className="container flex flex-col items-center justify-center gap-4 px-4 md:px-6 md:flex-row">
          <div className="flex gap-4">
            <p className="text-xs text-neutral-500">© 2025 Transinia. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
