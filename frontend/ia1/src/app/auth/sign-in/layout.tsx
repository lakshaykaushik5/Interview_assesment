import type { Metadata } from "next";
// import "./globals.css"
import { SessionProvider } from "next-auth/react";


export const metadata:Metadata = {
    title:"IA1",
    description:"IA1 Session"
}


export default function RootLayout({children}:{children:React.ReactNode}){
    return(
        <html lang="en">
            <body>
                <SessionProvider>
                    {children}
                </SessionProvider>
            </body>
        </html>
    )
}