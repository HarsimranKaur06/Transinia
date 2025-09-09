import Link from 'next/link';
import { ArrowLeft, FileText, ListChecks, User, Calendar, Clock } from 'lucide-react';

export default function DashboardPage() {
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
              className="text-sm font-medium underline underline-offset-4 font-semibold"
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
          <Link href="/" className="inline-flex items-center text-sm text-neutral-500 hover:text-neutral-900">
            <ArrowLeft className="mr-1 h-4 w-4" />
            Back to Home
          </Link>
          <h1 className="text-3xl font-bold mt-4">Meeting Insights Dashboard</h1>
          <p className="text-neutral-500 mt-2">View your meeting analytics and recent activity</p>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <div className="bg-white p-6 rounded-lg border flex flex-col">
            <div className="flex items-center mb-4">
              <div className="bg-neutral-100 p-2 rounded-md mr-3">
                <FileText className="h-5 w-5 text-neutral-700" />
              </div>
              <span className="text-neutral-500 text-sm">Total Meetings</span>
            </div>
            <span className="text-3xl font-bold">7</span>
          </div>
          
          <div className="bg-white p-6 rounded-lg border flex flex-col">
            <div className="flex items-center mb-4">
              <div className="bg-neutral-100 p-2 rounded-md mr-3">
                <ListChecks className="h-5 w-5 text-neutral-700" />
              </div>
              <span className="text-neutral-500 text-sm">Action Items</span>
            </div>
            <span className="text-3xl font-bold">21</span>
          </div>
          
          <div className="bg-white p-6 rounded-lg border flex flex-col">
            <div className="flex items-center mb-4">
              <div className="bg-neutral-100 p-2 rounded-md mr-3">
                <User className="h-5 w-5 text-neutral-700" />
              </div>
              <span className="text-neutral-500 text-sm">Participants</span>
            </div>
            <span className="text-3xl font-bold">3</span>
          </div>
          
          <div className="bg-white p-6 rounded-lg border flex flex-col">
            <div className="flex items-center mb-4">
              <div className="bg-neutral-100 p-2 rounded-md mr-3">
                <Clock className="h-5 w-5 text-neutral-700" />
              </div>
              <span className="text-neutral-500 text-sm">Pending Tasks</span>
            </div>
            <span className="text-3xl font-bold">9</span>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Recent Meetings */}
          <div className="bg-white p-6 rounded-lg border">
            <h2 className="text-xl font-semibold mb-4">Recent Meetings</h2>
            <div className="divide-y">
              <div className="py-4">
                <div className="flex items-center mb-2">
                  <Calendar className="h-4 w-4 text-neutral-400 mr-2" />
                  <span className="text-sm text-neutral-500">September 9, 2025</span>
                </div>
                <h3 className="font-medium mb-1">Product Planning Meeting</h3>
                <div className="flex gap-2">
                  <span className="bg-neutral-100 text-xs px-2 py-1 rounded-md">3 participants</span>
                  <span className="bg-neutral-100 text-xs px-2 py-1 rounded-md">4 action items</span>
                </div>
              </div>
              
              <div className="py-4">
                <div className="flex items-center mb-2">
                  <Calendar className="h-4 w-4 text-neutral-400 mr-2" />
                  <span className="text-sm text-neutral-500">September 5, 2025</span>
                </div>
                <h3 className="font-medium mb-1">Q3 Launch Planning</h3>
                <div className="flex gap-2">
                  <span className="bg-neutral-100 text-xs px-2 py-1 rounded-md">3 participants</span>
                  <span className="bg-neutral-100 text-xs px-2 py-1 rounded-md">5 action items</span>
                </div>
              </div>
              
              <div className="py-4">
                <div className="flex items-center mb-2">
                  <Calendar className="h-4 w-4 text-neutral-400 mr-2" />
                  <span className="text-sm text-neutral-500">August 24, 2025</span>
                </div>
                <h3 className="font-medium mb-1">Security Review</h3>
                <div className="flex gap-2">
                  <span className="bg-neutral-100 text-xs px-2 py-1 rounded-md">3 participants</span>
                  <span className="bg-neutral-100 text-xs px-2 py-1 rounded-md">3 action items</span>
                </div>
              </div>
            </div>
            <div className="mt-4">
              <Link 
                href="#" 
                className="text-sm font-medium text-neutral-900 hover:underline"
              >
                View all meetings
              </Link>
            </div>
          </div>

          {/* High Priority Tasks */}
          <div className="bg-white p-6 rounded-lg border">
            <h2 className="text-xl font-semibold mb-4">High Priority Tasks</h2>
            <div className="divide-y">
              <div className="py-4">
                <h3 className="font-medium mb-1">File a ticket for missing 2FA on admin dashboard</h3>
                <div className="flex items-center mb-2">
                  <User className="h-4 w-4 text-neutral-400 mr-2" />
                  <span className="text-sm text-neutral-500">Alex</span>
                  <div className="ml-auto flex items-center">
                    <Clock className="h-4 w-4 text-neutral-400 mr-1" />
                    <span className="text-sm text-neutral-500">Due: Oct 6, 2023</span>
                  </div>
                </div>
                <div className="flex">
                  <span className="bg-red-100 text-red-700 text-xs px-2 py-1 rounded-md">High Priority</span>
                </div>
              </div>
              
              <div className="py-4">
                <h3 className="font-medium mb-1">Update website copy with new pricing</h3>
                <div className="flex items-center mb-2">
                  <User className="h-4 w-4 text-neutral-400 mr-2" />
                  <span className="text-sm text-neutral-500">Priya</span>
                  <div className="ml-auto flex items-center">
                    <Clock className="h-4 w-4 text-neutral-400 mr-1" />
                    <span className="text-sm text-neutral-500">Due: TBD</span>
                  </div>
                </div>
                <div className="flex">
                  <span className="bg-red-100 text-red-700 text-xs px-2 py-1 rounded-md">High Priority</span>
                </div>
              </div>
              
              <div className="py-4">
                <h3 className="font-medium mb-1">Own risk register for Q3 launch</h3>
                <div className="flex items-center mb-2">
                  <User className="h-4 w-4 text-neutral-400 mr-2" />
                  <span className="text-sm text-neutral-500">Jordan</span>
                  <div className="ml-auto flex items-center">
                    <Clock className="h-4 w-4 text-neutral-400 mr-1" />
                    <span className="text-sm text-neutral-500">Due: TBD</span>
                  </div>
                </div>
                <div className="flex">
                  <span className="bg-red-100 text-red-700 text-xs px-2 py-1 rounded-md">High Priority</span>
                </div>
              </div>
            </div>
            <div className="mt-4">
              <Link 
                href="#" 
                className="text-sm font-medium text-neutral-900 hover:underline"
              >
                View all tasks
              </Link>
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
