import { getToken } from "next-auth/jwt";
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";
import { PrismaClient } from "@prisma/client";


const prisma = new PrismaClient()

export async function middleware(req:NextRequest){
    const token = await getToken({req,secret:process.env.NEXTAUTH_SECRET})
    const ip = req.headers.get("x-forwarded-for")?.split(",")[0]?.trim() || req.ip || ""

    if(token?.sub){
        // prisma.user.update({
        //     where:{id:token.sub},
        //     data:{ipAddress:ip},
        // }).catch(()=>{})
        console.log(" --ip-- ",ip)
    }

    // if(req.nextUrl.pathname.startsWith("/dashboard") && !token){
    //     const signInUrl = new URL("/api/auth/signin",req.url)
    //     return NextResponse.redirect(signInUrl)
    // }

    if(req.nextUrl.pathname === "/" && token){
        const dashboardUrl = new URL("/dashboard",req.url)
        return NextResponse.redirect(dashboardUrl)
    }

    return NextResponse.next()
}

export const config ={
    matcher:["/dashboard/:path*","/"]
}