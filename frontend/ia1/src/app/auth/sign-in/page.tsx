"use client"

import { LoginForm } from "@/components/login-form"
import { signIn, useSession } from "next-auth/react"
// import { useRouter } from "next/router";
import { useRouter } from "next/navigation";

import { useEffect } from "react";

export default function Page() {

  const {status} = useSession();
  const router = useRouter()

  useEffect(()=>{
    if(status === "authenticated"){
      router.replace("/dashboard")
    }else{
      router.replace("/auth/sign-in")
    }
  },[status,router])

  const onClickSignIn = ()=>{
    signIn('google')
  }

  return (
    <div className="flex min-h-svh w-full items-center justify-center p-6 md:p-10">
      <div className="w-full max-w-sm">
        <LoginForm onClickSignIn={onClickSignIn}/>
      </div>
    </div>
  )
}
