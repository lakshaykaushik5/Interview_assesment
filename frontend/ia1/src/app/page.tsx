import React from "react";
import Link from "next/link";


interface FeatureCardProps {
  title: string;
  description: string;
  icon: React.ReactNode;
}

const FeatureCard: React.FC<FeatureCardProps> = ({ title, description, icon }) => {
  return (
    <div className="bg-gray-800 rounded-xl p-6 shadow-lg flex flex-col items-center text-center space-y-4 
                    transition-transform transform hover:scale-105 hover:shadow-2xl cursor-pointer">
      <div className="transition-colors duration-300 hover:text-purple-400 hover:scale-110">
        {icon}
      </div>
      <h3 className="text-xl font-semibold">{title}</h3>
      <p className="text-gray-400">{description}</p>
    </div>
  );
};

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-tr from-gray-900 via-purple-900 to-indigo-900 text-white font-sans">
      {/* Header with logo and product name */}
      <header className="flex items-center gap-3 p-6 max-w-7xl mx-auto">
        {/* Inline SVG Logo */}
        <svg
          width="40"
          height="40"
          viewBox="0 0 24 24"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          className="text-purple-400 transition-colors duration-300 hover:text-purple-600"
        >
          <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2" />
          <path
            d="M8 12l2 2 4-4"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>

        <h1 className="text-3xl font-bold tracking-wide">IA1</h1>
      </header>

      {/* Hero Section */}
      <section className="flex flex-col items-center justify-center text-center px-6 py-20 max-w-4xl mx-auto space-y-6">
        <h2 className="text-5xl font-extrabold leading-tight">
          Practice Interviews with AI and Get Instant Feedback
        </h2>
        <p className="text-lg max-w-xl text-purple-300">
          IA1 is an AI-powered interview platform. Simulate real interviews and improve quickly. Currently in beta.
        </p>
        <Link href={"auth/sign-in"}>
          <button className="bg-purple-600 hover:bg-purple-700 transition-shadow rounded-full px-10 py-3 text-white font-semibold shadow-lg hover:shadow-2xl">
            Try the Beta
          </button>
        </Link>

        {/* Placeholder Hero Illustration */}
        <div className="mt-12 w-full max-w-lg aspect-video bg-gradient-to-r from-purple-700 to-indigo-700 rounded-xl shadow-xl flex items-center justify-center">
          <svg
            width="150"
            height="150"
            viewBox="0 0 24 24"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
            className="text-white opacity-60"
          >
            <rect x="3" y="3" width="18" height="18" rx="3" stroke="currentColor" strokeWidth="2" />
            <path d="M8 12h8" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
            <path d="M12 8v8" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
          </svg>
        </div>
      </section>

      {/* Features Section */}
      <section className="max-w-6xl mx-auto px-6 py-20 grid grid-cols-1 md:grid-cols-3 gap-10">
        <FeatureCard
          title="Simulate Real Interviews"
          description="Practice with realistic questions tailored for your field."
          icon={
            <svg
              className="w-12 h-12 text-indigo-400"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              viewBox="0 0 24 24"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 14l9-5-9-5-9 5 9 5z" />
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 14l6.16-3.422a12.083 12.083 0 010 6.844L12 14z" />
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 14v7" />
            </svg>
          }
        />
        <FeatureCard
          title="Instant AI Feedback"
          description="Get detailed feedback to know exactly where to improve."
          icon={
            <svg
              className="w-12 h-12 text-purple-400"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              viewBox="0 0 24 24"
              xmlns="http://www.w3.org/2000/svg"
            >
              <circle cx="12" cy="12" r="3" />
              <path strokeLinecap="round" strokeLinejoin="round" d="M19.4 15a7.97 7.97 0 010-6" />
              <path strokeLinecap="round" strokeLinejoin="round" d="M4.6 9a7.973 7.973 0 010 6" />
              <path strokeLinecap="round" strokeLinejoin="round" d="M15 3.6v16.8" />
            </svg>
          }
        />
        <FeatureCard
          title="Track Your Progress"
          description="Visualize your improvements over sessions, stay motivated."
          icon={
            <svg
              className="w-12 h-12 text-pink-400"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              viewBox="0 0 24 24"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path strokeLinecap="round" strokeLinejoin="round" d="M3 3v18h18" />
              <path strokeLinecap="round" strokeLinejoin="round" d="M9 9l3 3-3 3" />
            </svg>
          }
        />
      </section>

      {/* Beta Notification */}
      <section className="bg-purple-800 text-center text-purple-200 py-8 px-6 max-w-3xl mx-auto rounded-xl">
        <p className="font-semibold text-lg">
          ⚠️ IA1 is currently in Beta. Your feedback helps shape the future of AI interview coaching!
        </p>
      </section>

      {/* Footer */}
      <footer className="text-center py-10 text-gray-400">
        <p>© 2025 IA1 • Built with ❤️ for interview success</p>
        <p>
          Contact: <a href="mailto:info@ia1.com" className="underline hover:text-white">info@ia1.com</a>
        </p>
      </footer>
    </main>
  );
}
