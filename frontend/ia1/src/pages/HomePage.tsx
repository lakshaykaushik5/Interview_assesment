"use client";
import React from "react";

interface FeatureCardProps {
  title: string;
  description: string;
  icon: React.ReactNode;
}

const FeatureCard: React.FC<FeatureCardProps> = ({ title, description, icon }) => (
  <div className="bg-gray-800 rounded-xl p-6 shadow-lg flex flex-col items-center text-center space-y-4
                  transition-transform transform hover:scale-105 hover:shadow-2xl cursor-pointer">
    <div className="transition-colors duration-300 hover:text-purple-400 hover:scale-110">{icon}</div>
    <h3 className="text-xl font-semibold">{title}</h3>
    <p className="text-gray-400">{description}</p>
  </div>
);

export default function HomePage() {
  const handleGoogleSignIn = () => {
    alert("Google Sign-in clicked! Integrate auth here.");
  };

  return (
    <main
      className="min-h-screen bg-gradient-to-tr from-gray-900 via-purple-900 to-indigo-900 text-white font-sans
                  relative overflow-hidden"
      style={{ backgroundSize: "200% 200%", animation: "gradientShift 15s ease infinite" }}
    >
      {/* Navbar */}
      <nav className="flex items-center justify-between max-w-7xl mx-auto px-6 py-4 sticky top-0 bg-gray-900/70 backdrop-blur-md z-20">
        <div className="flex items-center gap-3">
          {/* Inline SVG Logo */}
          <svg
            width="36"
            height="36"
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
          <h1 className="text-2xl font-bold tracking-wide">IA1</h1>
        </div>

        <button
          onClick={handleGoogleSignIn}
          className="bg-white text-purple-700 font-semibold px-5 py-2 rounded-full shadow-md
                     hover:bg-purple-100 transition-colors flex items-center gap-2"
        >
          {/* Google Icon */}
          <svg
            width="18"
            height="18"
            viewBox="0 0 533.5 544.3"
            xmlns="http://www.w3.org/2000/svg"
            className="w-5 h-5"
          >
            <path fill="#4285F4" d="M533.5 278.4c0-18.6-1.5-36.5-4.3-53.9H272v101.5h147.4c-6.3 33.8-25 62.4-53.4 81.6v67h86.5c50.5-46.5 79.5-115 79.5-195.2z" />
            <path fill="#34A853" d="M272 544.3c72.6 0 133.6-24 178.1-65.1l-86.5-67c-23.9 16-54.4 25.3-91.6 25.3-70.5 0-130.3-47.5-151.7-111.3h-89.9v69.8c44.3 87.1 134.9 148.3 241.6 148.3z" />
            <path fill="#FBBC05" d="M120.3 325.2c-10.8-32-10.8-66.7 0-98.7v-69.8h-89.9c-39.3 77.3-39.3 169.4 0 246.7l89.9-68.2z" />
            <path fill="#EA4335" d="M272 107.7c39.4 0 75 13.6 102.8 40.3l77-77C400.7 24.9 341 0 272 0 165.3 0 74.7 61.2 30.3 148.3l89.9 69.8c21.4-63.8 81.2-111.3 151.8-111.3z" />
          </svg>
          Sign in with Google
        </button>
      </nav>

      {/* Content */}
      <section className="flex flex-col items-center justify-center text-center px-6 py-20 max-w-4xl mx-auto space-y-6 z-10 relative">
        <h2 className="text-5xl font-extrabold leading-tight">
          Practice Interviews with AI and Get Instant Feedback
        </h2>
        <p className="text-lg max-w-xl text-purple-300">
          IA1 is an AI-powered interview platform. Simulate real interviews and improve quickly. Currently in beta.
        </p>
        <button className="bg-purple-600 hover:bg-purple-700 transition-shadow rounded-full px-10 py-3 text-white font-semibold shadow-lg">
          Try the Beta
        </button>
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
      <section className="max-w-6xl mx-auto px-6 py-20 grid grid-cols-1 md:grid-cols-3 gap-10 z-10 relative">
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
      <section className="bg-purple-800 text-center text-purple-200 py-8 px-6 max-w-3xl mx-auto rounded-xl z-10 relative">
        <p className="font-semibold text-lg">
          ⚠️ IA1 is currently in Beta. Your feedback helps shape the future of AI interview coaching!
        </p>
      </section>

      {/* Footer */}
      <footer className="text-center py-10 text-gray-400 z-10 relative">
        <p>© 2025 IA1 • Built with ❤️ for interview success</p>
        <p>
          Contact: <a href="mailto:info@ia1.com" className="underline hover:text-white">info@ia1.com</a>
        </p>
      </footer>

      {/* Background Animation Keyframes */}
      <style jsx>{`
        @keyframes gradientShift {
          0% {
            background-position: 0% 50%;
          }
          50% {
            background-position: 100% 50%;
          }
          100% {
            background-position: 0% 50%;
          }
        }
      `}</style>
    </main>
  );
}
