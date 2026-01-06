"use client";

import { useEKYCStore } from "../../stores/ekyc-store";

const progressLabels: Record<string, { label: string; color: string }> = {
    idle: { label: "Idle", color: "bg-gray-500" },
    id_uploading: { label: "ID Uploading", color: "bg-blue-500" },
    id_scanned: { label: "ID Scanned", color: "bg-yellow-500" },
    face_verifying: { label: "Face Verifying", color: "bg-orange-500" },
};

export function Header() {
    const { progress, idCardUrl } = useEKYCStore();
    const statusInfo = progressLabels[progress] || progressLabels.idle;

    return (
        <header className="border-b border-border bg-card">
            <div className="flex items-center justify-between p-4 max-w-4xl mx-auto">
                <div className="flex-1" />
                <div className="text-center">
                    <h1 className="text-xl font-semibold">ລະບົບຢັ້ງຢືນຕົວຕົນ eKYC</h1>
                    <p className="text-sm text-muted-foreground">ຂະບວນການຢັ້ງຢືນບັດປະຈຳຕົວທີ່ປອດໄພ</p>
                </div>
                <div className="flex-1 flex justify-end">
                    <div className="text-xs space-y-1">
                        <div className={`${statusInfo.color} text-white px-2 py-1 rounded-full text-center`}>{statusInfo.label}</div>
                        {idCardUrl && (
                            <div className="text-muted-foreground truncate max-w-[120px]" title={idCardUrl}>
                                ID: ...{idCardUrl.slice(-20)}
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </header>
    );
}
