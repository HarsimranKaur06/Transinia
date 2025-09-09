import Link from 'next/link';
import { ArrowRight, FileText, ListChecks, Users } from 'lucide-react';

export default function Home() {
  return (
    <div className="flex flex-col min-h-screen">
      {/* Navigation */}
      <header className="border-b">
        <div className="container mx-auto flex h-16 items-center justify-between px-4">
          <div className="flex items-center gap-2">
            <span className="text-2xl font-bold">Transinia</span>
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

      {/* Hero Section */}
      <section className="w-full py-12 md:py-24 lg:py-32 bg-neutral-50">
        <div className="container px-4 md:px-6 mx-auto">
          <div className="grid gap-6 lg:grid-cols-2 lg:gap-12 items-center">
            <div className="flex flex-col justify-center space-y-4">
              <div className="space-y-2">
                <h1 className="text-3xl font-bold tracking-tighter sm:text-5xl xl:text-6xl/none">
                  Transform Meeting Chaos into Actionable Clarity
                </h1>
                <p className="max-w-[600px] text-neutral-500 md:text-xl">
                  AI-powered meeting transcript analysis that extracts decisions, action items, and key insights in seconds
                </p>
              </div>
              <div className="flex flex-col gap-2 min-[400px]:flex-row">
                <Link
                  href="/transcripts"
                  className="inline-flex h-10 items-center justify-center rounded-md bg-neutral-900 px-8 text-sm font-medium text-neutral-50 shadow transition-colors hover:bg-neutral-900/90 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-neutral-950"
                >
                  Analyze Your Transcript
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Link>
              </div>
            </div>
            <div className="flex justify-center">
              <div className="relative w-full max-w-[500px]">
                {/* Placeholder for illustration */}
                <div className="aspect-video overflow-hidden rounded-xl bg-neutral-100 object-cover object-center border border-neutral-200 flex items-center justify-center p-6">
                  <div className="text-center">
                    <FileText className="h-16 w-16 mx-auto mb-4 text-neutral-400" />
                    <p className="text-neutral-500">Transcript to Insights Visualization</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="w-full py-12 md:py-24 lg:py-32">
        <div className="container px-4 md:px-6 mx-auto">
          <div className="flex flex-col items-center justify-center space-y-4 text-center">
            <div className="space-y-2">
              <h2 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl">Features</h2>
              <p className="max-w-[900px] text-neutral-500 md:text-xl/relaxed lg:text-base/relaxed xl:text-xl/relaxed">
                Powerful tools to transform your meeting transcripts into actionable insights
              </p>
            </div>
          </div>
          <div className="mx-auto grid max-w-5xl grid-cols-1 gap-6 md:grid-cols-3 lg:gap-12 mt-12">
            {/* Feature 1 */}
            <div className="flex flex-col items-center space-y-4 text-center">
              <div className="flex h-16 w-16 items-center justify-center rounded-full bg-neutral-100">
                <ListChecks className="h-8 w-8 text-neutral-900" />
              </div>
              <div className="space-y-2">
                <h3 className="text-xl font-bold">Extract Action Items</h3>
                <p className="text-sm text-neutral-500">
                  Automatically identify and track action items with assigned owners and due dates
                </p>
              </div>
            </div>
            
            {/* Feature 2 */}
            <div className="flex flex-col items-center space-y-4 text-center">
              <div className="flex h-16 w-16 items-center justify-center rounded-full bg-neutral-100">
                <FileText className="h-8 w-8 text-neutral-900" />
              </div>
              <div className="space-y-2">
                <h3 className="text-xl font-bold">Identify Key Decisions</h3>
                <p className="text-sm text-neutral-500">
                  Never lose track of important decisions made during meetings
                </p>
              </div>
            </div>
            
            {/* Feature 3 */}
            <div className="flex flex-col items-center space-y-4 text-center">
              <div className="flex h-16 w-16 items-center justify-center rounded-full bg-neutral-100">
                <Users className="h-8 w-8 text-neutral-900" />
              </div>
              <div className="space-y-2">
                <h3 className="text-xl font-bold">Track Participants</h3>
                <p className="text-sm text-neutral-500">
                  Identify participant contributions and search meetings by participant
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="w-full py-12 md:py-24 lg:py-32 bg-neutral-50">
        <div className="container px-4 md:px-6 mx-auto">
          <div className="flex flex-col items-center justify-center space-y-4 text-center">
            <div className="space-y-2">
              <h2 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl">How It Works</h2>
              <p className="max-w-[900px] text-neutral-500 md:text-xl/relaxed lg:text-base/relaxed xl:text-xl/relaxed">
                Three simple steps to transform your meeting transcripts
              </p>
            </div>
          </div>
          <div className="mx-auto grid max-w-5xl grid-cols-1 gap-6 md:grid-cols-3 lg:gap-12 mt-12">
            {/* Step 1 */}
            <div className="flex flex-col items-center space-y-4 text-center">
              <div className="flex h-12 w-12 items-center justify-center rounded-full bg-neutral-900 text-white font-bold text-xl">
                1
              </div>
              <div className="space-y-2">
                <h3 className="text-xl font-bold">Upload or Select</h3>
                <p className="text-sm text-neutral-500">
                  Upload a new meeting transcript or select from existing ones
                </p>
              </div>
            </div>
            
            {/* Step 2 */}
            <div className="flex flex-col items-center space-y-4 text-center">
              <div className="flex h-12 w-12 items-center justify-center rounded-full bg-neutral-900 text-white font-bold text-xl">
                2
              </div>
              <div className="space-y-2">
                <h3 className="text-xl font-bold">AI Analysis</h3>
                <p className="text-sm text-neutral-500">
                  Our AI analyzes the content to extract key information
                </p>
              </div>
            </div>
            
            {/* Step 3 */}
            <div className="flex flex-col items-center space-y-4 text-center">
              <div className="flex h-12 w-12 items-center justify-center rounded-full bg-neutral-900 text-white font-bold text-xl">
                3
              </div>
              <div className="space-y-2">
                <h3 className="text-xl font-bold">Review Results</h3>
                <p className="text-sm text-neutral-500">
                  View organized meeting minutes, decisions, and action items
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="w-full py-12 md:py-24 lg:py-32">
        <div className="container px-4 md:px-6 mx-auto">
          <div className="flex flex-col items-center justify-center space-y-4 text-center">
            <div className="space-y-2">
              <h2 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl">Ready to Get Started?</h2>
              <p className="max-w-[900px] text-neutral-500 md:text-xl/relaxed lg:text-base/relaxed xl:text-xl/relaxed">
                Start analyzing your meeting transcripts today
              </p>
            </div>
            <div className="flex flex-col gap-2 min-[400px]:flex-row">
              <Link
                href="/transcripts"
                className="inline-flex h-10 items-center justify-center rounded-md bg-neutral-900 px-8 text-sm font-medium text-neutral-50 shadow transition-colors hover:bg-neutral-900/90 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-neutral-950"
              >
                Try It Now
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t py-6 md:py-8">
        <div className="container flex flex-col items-center justify-center gap-4 px-4 md:px-6 md:flex-row">
          <div className="flex gap-4">
            <p className="text-xs text-neutral-500">© 2025 Transinia. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
