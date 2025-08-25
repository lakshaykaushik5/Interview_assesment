import NextAuth from "next-auth";
import GoogleProvider from "next-auth/providers/google";
// import {PrismaAdapter} from "@next-auth/prisma-adapter"
// import { PrismaAdapter } from "@next-auth/prisma-adapter";
import {PrismaAdapter} from "@next-auth/prisma-adapter"

import {PrismaClient} from "@prisma/client"


const prisma = new PrismaClient()

export const handler = NextAuth({
    adapter:PrismaAdapter(prisma),
    providers:[
        GoogleProvider({
            clientId:process.env.GOOGLE_CLIENT_ID!,
            clientSecret:process.env.GOOGLE_CLIENT_SECRET!,
        }),

    ],
    secret:process.env.NEXTAUTH_SECRET,
    session:{
        strategy:"jwt"
    },

    callbacks:{
        async jwt({token,user}){
            if(user) token.id=user.id
            return token
        },
        async session({session,token}){
            if(session.user) session.user.id = token.id as string
            return session
        },
    },
    debug:process.env.NODE_ENV == "development",
});

export { handler as GET, handler as POST };
