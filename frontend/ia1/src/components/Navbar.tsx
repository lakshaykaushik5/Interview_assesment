"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useUser, SignInButton, SignOutButton } from "@clerk/nextjs";

export default function Navbar() {
  const pathname = usePathname();
  const { isSignedIn, isLoaded } = useUser();

  // Don’t show on homepage ("/")
  if (pathname === "/") return null;

  // Nav links example - add as needed
  const navLinks = [
    { label: "Dashboard", href: "/dashboard" },
    { label: "Profile", href: "/profile" },
    { label: "Settings", href: "/settings" },
  ];

  const isActive = (href: string) => pathname === href;

  return (
    <nav className="bg-gray-900 text-white p-4 flex justify-between items-center max-w-7xl mx-auto sticky top-0 z-50 shadow-md">
      <div className="flex items-center space-x-6">
        <Link href="/dashboard" className="flex items-center space-x-2">
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
          <span className="text-2xl font-bold text-purple-400">IA1</span>
        </Link>

        {/* <ul className="flex space-x-4">
          {navLinks.map(({ href, label }) => (
            <li key={href}>
              <Link
                href={href}
                className={`hover:text-purple-400 transition ${
                  isActive(href) ? "text-purple-500 font-semibold underline" : ""
                }`}
              >
                {label}
              </Link>
            </li>
          ))}
        </ul> */}
      </div>

      <div>
        {!isLoaded ? null : isSignedIn ? (
          <SignOutButton>
            <button className="bg-red-600 px-5 py-2 rounded-lg text-white hover:bg-red-700 transition">
              Logout
            </button>
          </SignOutButton>
        ) : (
          <SignInButton>
            <button className="bg-green-600 px-5 py-2 rounded-lg text-white hover:bg-green-700 transition">
              Login
            </button>
          </SignInButton>
        )}
      </div>
    </nav>
  );
}
