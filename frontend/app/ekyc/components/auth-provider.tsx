"use client";

import { useEffect, useState } from "react";
import { useRouter, usePathname } from "next/navigation";
import { useAuthStore } from "../stores/auth-store";

interface AuthProviderProps {
    children: React.ReactNode;
}

// Routes that don't require authentication
const PUBLIC_ROUTES = ["/login", "/register"];

export function AuthProvider({ children }: AuthProviderProps) {
    const router = useRouter();
    const pathname = usePathname();
    const { isAuthenticated, checkAuth } = useAuthStore();
    const [isChecking, setIsChecking] = useState(true);

    useEffect(() => {
        // Check if user is authenticated from localStorage
        checkAuth();
        setIsChecking(false);
    }, [checkAuth]);

    useEffect(() => {
        if (isChecking) return;

        const isPublicRoute = PUBLIC_ROUTES.some((route) => pathname?.startsWith(route));

        if (!isAuthenticated && !isPublicRoute && pathname !== "/") {
            // Redirect to login if trying to access protected route
            router.push("/login");
        }
    }, [isAuthenticated, pathname, router, isChecking]);

    if (isChecking) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-background">
                <div className="text-muted-foreground">Dang tai...</div>
            </div>
        );
    }

    return <>{children}</>;
}
