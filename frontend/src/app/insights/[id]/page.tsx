"use client";

import Link from 'next/link';
import { ArrowLeft, Users, Clock, FileText, CheckCircle, AlertCircle, RefreshCw, Download, Save } from 'lucide-react';
import { useState, useEffect } from 'react';
import { Insight, ActionItem } from '@/types';
import { getInsight } from '@/lib/api';

// Sample insight data (will be replaced with API data in production)
const sampleInsight: Insight = {
  id: '1',
  title: 'Product Planning Meeting',
  date: 'September 10, 2025',
  summary: 'The team discussed the Q4 roadmap and prioritized features for the next release. Key decisions were made about resource allocation and timeline adjustments to accommodate the new security requirements.',
  actionItems: [
    { id: '1', text: 'Update the project timeline document', assignee: 'Sarah', completed: true },
    { id: '2', text: 'Schedule follow-up meeting with design team', assignee: 'Michael', completed: false },
    { id: '3', text: 'Create detailed specs for the new authentication flow', assignee: 'David', completed: false },
    { id: '4', text: 'Share meeting notes with stakeholders', completed: true }
  ],
  keyPoints: [
    'Q4 roadmap will focus on security and performance improvements',
    'New authentication system to be implemented by end of November',
    'Customer feedback highlighted need for improved dashboard analytics',
    'Budget approval for additional QA resources confirmed',
    'Integration with third-party payment processor to be completed in Q1 next year'
  ],
  participants: ['John Doe', 'Sarah Smith', 'Michael Johnson', 'David Lee', 'Emma Wilson'],
  duration: '45 minutes'
};

export default function InsightPage({ params }: { params: { id: string } }) {
  const [insight, setInsight] = useState<Insight | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadInsight() {
      try {
        setIsLoading(true);
        
        // Try to fetch from the API
        try {
          const result = await getInsight(params.id);
          if (result.success && result.insight) {
            setInsight(result.insight);
          } else {
            throw new Error(result.message || 'Failed to load insights');
          }
        } catch (e) {
          console.log("API not available, using sample data");
          // For development, use sample data
          setTimeout(() => {
            setInsight({
              ...sampleInsight,
              id: params.id
            });
          }, 1000);
        }
      } catch (err) {
        setError('Failed to load meeting insights. Please try again.');
        console.error('Error loading insights:', err);
      } finally {
        setIsLoading(false);
      }
    }

    loadInsight();
  }, [params.id]);

  const toggleActionItem = (id: string) => {
    if (!insight) return;
    
    setInsight({
      ...insight,
      actionItems: insight.actionItems.map(item => 
        item.id === id ? { ...item, completed: !item.completed } : item
      )
    });
  };
  
  const downloadMinutes = () => {
    if (!insight) return;
    
    // Create markdown content for download
    const markdownContent = `# ${insight.title}\n\n` +
      `Date: ${insight.date}\n\n` +
      `## Summary\n\n${insight.summary}\n\n` +
      `## Key Points\n\n${insight.keyPoints.map(point => `- ${point}`).join('\n')}\n\n` +
      `## Action Items\n\n${insight.actionItems.map(item => 
        `- [${item.completed ? 'x' : ' '}] ${item.text}${item.assignee ? ` (Assigned to: ${item.assignee})` : ''}`
      ).join('\n')}\n\n` +
      `## Participants\n\n${insight.participants.map(p => `- ${p}`).join('\n')}\n\n`;
    
    // Create and trigger download
    const blob = new Blob([markdownContent], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${insight.title.replace(/\s+/g, '-').toLowerCase()}-minutes.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };
  
  const downloadJson = () => {
    if (!insight) return;
    
    // Create JSON content for download
    const jsonContent = JSON.stringify({
      meeting: {
        id: insight.id,
        title: insight.title,
        date: insight.date,
        summary: insight.summary,
        keyPoints: insight.keyPoints,
        actionItems: insight.actionItems,
        participants: insight.participants
      }
    }, null, 2);
    
    // Create and trigger download
    const blob = new Blob([jsonContent], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${insight.title.replace(/\s+/g, '-').toLowerCase()}-data.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  if (isLoading) {
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
                href="/dashboard" 
                className="text-sm font-medium hover:underline underline-offset-4"
              >
                Dashboard
              </Link>
              <Link 
                href="/transcripts" 
                className="text-sm font-medium hover:underline underline-offset-4"
              >
                Transcripts
              </Link>
            </nav>
          </div>
        </header>
        
        <div className="flex items-center justify-center flex-grow">
          <div className="text-center p-8">
            <RefreshCw className="h-12 w-12 text-neutral-400 animate-spin mx-auto mb-4" />
            <h2 className="text-xl font-semibold mb-2">Loading meeting insights...</h2>
            <p className="text-neutral-500">Please wait while we prepare your meeting summary</p>
          </div>
        </div>
      </div>
    );
  }

  if (error || !insight) {
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
                href="/dashboard" 
                className="text-sm font-medium hover:underline underline-offset-4"
              >
                Dashboard
              </Link>
              <Link 
                href="/transcripts" 
                className="text-sm font-medium hover:underline underline-offset-4"
              >
                Transcripts
              </Link>
            </nav>
          </div>
        </header>
        
        <div className="flex items-center justify-center flex-grow">
          <div className="text-center p-8 max-w-md">
            <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
            <h2 className="text-xl font-semibold mb-2">Something went wrong</h2>
            <p className="text-neutral-500 mb-6">{error || 'Failed to load meeting insights. Please try again.'}</p>
            <Link 
              href="/transcripts" 
              className="inline-flex h-10 items-center justify-center rounded-md bg-neutral-900 px-8 text-sm font-medium text-neutral-50 shadow transition-colors hover:bg-neutral-900/90"
            >
              Back to Transcripts
            </Link>
          </div>
        </div>
      </div>
    );
  }

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
              href="/dashboard" 
              className="text-sm font-medium hover:underline underline-offset-4"
            >
              Dashboard
            </Link>
            <Link 
              href="/transcripts" 
              className="text-sm font-medium hover:underline underline-offset-4"
            >
              Transcripts
            </Link>
          </nav>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <Link href="/transcripts" className="inline-flex items-center text-sm text-neutral-500 hover:text-neutral-900">
            <ArrowLeft className="mr-1 h-4 w-4" />
            Back to Transcripts
          </Link>
          <h1 className="text-3xl font-bold mt-4">{insight.title}</h1>
          <div className="flex flex-wrap items-center gap-4 mt-2">
            <p className="text-neutral-500">{insight.date}</p>
            <div className="flex items-center text-neutral-500">
              <Clock className="h-4 w-4 mr-1" />
              <span>{insight.duration}</span>
            </div>
            <div className="flex items-center text-neutral-500">
              <Users className="h-4 w-4 mr-1" />
              <span>{insight.participants.length} participants</span>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Summary Section */}
          <div className="lg:col-span-2">
            <div className="bg-white p-6 rounded-lg border mb-8">
              <h2 className="text-xl font-semibold mb-4">Meeting Summary</h2>
              <p className="text-neutral-700 leading-relaxed">{insight.summary}</p>
            </div>

            <div className="bg-white p-6 rounded-lg border">
              <h2 className="text-xl font-semibold mb-4">Key Points</h2>
              <ul className="space-y-3">
                {insight.keyPoints.map((point, index) => (
                  <li key={index} className="flex">
                    <div className="mr-3 mt-1 flex-shrink-0">
                      <div className="h-2 w-2 rounded-full bg-neutral-900"></div>
                    </div>
                    <p className="text-neutral-700">{point}</p>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-8">
            <div className="bg-white p-6 rounded-lg border">
              <h2 className="text-xl font-semibold mb-4">Action Items</h2>
              <ul className="space-y-3">
                {insight.actionItems.map((item) => (
                  <li key={item.id} className="flex items-start">
                    <button 
                      onClick={() => toggleActionItem(item.id)} 
                      className={`mr-3 mt-1 flex-shrink-0 h-5 w-5 rounded-full border flex items-center justify-center ${
                        item.completed 
                          ? 'bg-green-100 border-green-500 text-green-500' 
                          : 'border-neutral-300'
                      }`}
                    >
                      {item.completed && <CheckCircle className="h-4 w-4" />}
                    </button>
                    <div>
                      <p className={`text-neutral-700 ${item.completed ? 'line-through text-neutral-400' : ''}`}>{item.text}</p>
                      {item.assignee && (
                        <p className="text-sm text-neutral-500 mt-1">Assigned to: {item.assignee}</p>
                      )}
                    </div>
                  </li>
                ))}
              </ul>
            </div>

            <div className="bg-white p-6 rounded-lg border">
              <h2 className="text-xl font-semibold mb-4">Participants</h2>
              <ul className="space-y-2">
                {insight.participants.map((participant, index) => (
                  <li key={index} className="flex items-center">
                    <div className="mr-3 h-8 w-8 rounded-full bg-neutral-200 flex items-center justify-center">
                      <span className="text-sm font-medium">{participant.split(' ').map(n => n[0]).join('')}</span>
                    </div>
                    <p className="text-neutral-700">{participant}</p>
                  </li>
                ))}
              </ul>
            </div>
            
            <div className="bg-white p-6 rounded-lg border">
              <h2 className="text-xl font-semibold mb-4">Original Transcript</h2>
              <div className="flex items-center">
                <FileText className="h-5 w-5 text-neutral-400 mr-2" />
                <span className="text-neutral-700">transcript.txt</span>
                <Link 
                  href="#" 
                  className="ml-auto text-sm text-blue-600 hover:text-blue-800 hover:underline"
                >
                  View
                </Link>
              </div>
            </div>
            
            <div className="bg-white p-6 rounded-lg border">
              <h2 className="text-xl font-semibold mb-4">Download Options</h2>
              <div className="space-y-3">
                <button 
                  onClick={downloadMinutes}
                  className="w-full flex items-center justify-between p-3 bg-neutral-100 hover:bg-neutral-200 rounded-md transition-colors"
                >
                  <div className="flex items-center">
                    <Download className="h-5 w-5 text-neutral-600 mr-2" />
                    <span className="font-medium">Download as Markdown</span>
                  </div>
                  <span className="text-xs text-neutral-500">.md</span>
                </button>
                
                <button 
                  onClick={downloadJson}
                  className="w-full flex items-center justify-between p-3 bg-neutral-100 hover:bg-neutral-200 rounded-md transition-colors"
                >
                  <div className="flex items-center">
                    <Save className="h-5 w-5 text-neutral-600 mr-2" />
                    <span className="font-medium">Download as JSON</span>
                  </div>
                  <span className="text-xs text-neutral-500">.json</span>
                </button>
              </div>
              <p className="text-xs text-neutral-500 mt-3">
                Note: Meeting data is automatically saved to S3
              </p>
            </div>
          </div>
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
