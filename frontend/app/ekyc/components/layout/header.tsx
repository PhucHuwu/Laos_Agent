"use client";

import { useRouter } from "next/navigation";
import { useEKYCStore } from "../../stores/ekyc-store";
import { useAuthStore } from "../../stores/auth-store";

const progressLabels: Record<string, { label: string; color: string }> = {
    idle: { label: "Idle", color: "bg-gray-500" },
    id_uploading: { label: "ID Uploading", color: "bg-blue-500" },
    id_scanned: { label: "ID Scanned", color: "bg-yellow-500" },
    face_verifying: { label: "Face Verifying", color: "bg-orange-500" },
};

export function Header() {
    const router = useRouter();
    const { progress, idCardUrl } = useEKYCStore();
    const { user, logout } = useAuthStore();
    const statusInfo = progressLabels[progress] || progressLabels.idle;

    const handleLogout = () => {
        logout();
        router.push("/login");
    };

    return (
        <header className="border-b border-border bg-card">
            <div className="flex items-center justify-between p-4 max-w-4xl mx-auto">
                <div className="flex items-center gap-2">
                    {user?.isVerified && <span className="text-xs px-2 py-1 rounded-full bg-green-500/20 text-green-600">Verified</span>}
                </div>
                <div className="text-center">
                    <h1 className="text-xl font-semibold">eKYC Laos</h1>
                    <p className="text-sm text-muted-foreground">Xác minh danh tính điện tử</p>
                </div>
                <div className="flex items-center gap-3">
                    <div className="text-xs space-y-1">
                        <div className={`${statusInfo.color} text-white px-2 py-1 rounded-full text-center`}>{statusInfo.label}</div>
                    </div>
                    <button onClick={handleLogout} className="px-3 py-1.5 text-sm rounded-lg border border-border hover:bg-muted transition-colors">
                        Đăng xuất
                    </button>
                </div>
            </div>
        </header>
    );
}
