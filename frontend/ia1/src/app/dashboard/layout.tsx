"use client"

import { Navbar } from "@/components/Navbar";
import type { Metadata } from "next";
import { NavbarProvider, useNavbarContext } from "../states/NavbarContext";
// import "./globals.css"
import { SessionProvider } from "next-auth/react";


// export const metadata:Metadata = {
//     title:"IA1",
//     description:"IA1 Session"
// }

function LayoutContent({ children }: { children: React.ReactNode }) {
    const { onNavbarClick } = useNavbarContext()

    return (
        <>
            <Navbar onNavbarClick={onNavbarClick}/>
            <main>{children}</main>
        </>
    )
}


export default function RootLayout({ children }: { children: React.ReactNode }) {
    return (
        <html lang="en">
            <body>
                <NavbarProvider>
                    <LayoutContent>{children}</LayoutContent>
                </NavbarProvider>
            </body>
        </html>
    )
}