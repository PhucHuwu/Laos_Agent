"use client";

import { useEKYCStore } from "../../stores/ekyc-store";
import { useUIStore } from "../../stores/ui-store";
import { ThemeToggle } from "@/components/theme-toggle";

const progressLabels: Record<string, { label: string; color: string }> = {
    idle: { label: "Idle", color: "bg-gray-500" },
    id_uploading: { label: "ID Uploading", color: "bg-blue-500" },
    id_scanned: { label: "ID Scanned", color: "bg-yellow-500" },
    face_verifying: { label: "Face Verifying", color: "bg-orange-500" },
};

export function Header() {
    const { progress, idCardUrl } = useEKYCStore();
    const { toggleSidebar } = useUIStore();
    const statusInfo = progressLabels[progress] || progressLabels.idle;

    return (
        <header className="border-b border-border bg-card">
            <div className="flex items-center justify-between p-4 max-w-4xl mx-auto">
                {/* Left: Mobile menu button - Arrow icon */}
                <div className="flex items-center gap-2">
                    <button onClick={toggleSidebar} className="p-2 rounded-lg hover:bg-muted transition-colors md:hidden" aria-label="Open sidebar">
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                        </svg>
                    </button>
                </div>
                {/* Center: Title */}
                <div className="text-center">
                    <h1 className="text-xl font-semibold">eKYC Laos</h1>
                    <p className="text-sm text-muted-foreground hidden sm:block">ການຢັ້ງຢືນຕົວຕົນທາງເອເລັກໂຕຣນິກ</p>
                </div>
                {/* Right: Status + Theme toggle */}
                <div className="flex items-center gap-2 sm:gap-3">
                    <div className={`${statusInfo.color} text-white px-2 py-1 rounded-full text-center text-xs`}>{statusInfo.label}</div>
                    <ThemeToggle />
                </div>
            </div>
        </header>
    );
}
