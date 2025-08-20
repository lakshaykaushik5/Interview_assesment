import { SignIn } from "@clerk/nextjs";

export default function SignInPage() {
  return (
    <div className="custom-signin-page">
      {/* Your own header and styling */}
      <h1>Welcome Back! Please Sign In</h1>
      
      {/* Clerk’s sign-in UI */}
      <SignIn />
    </div>
  );
}
