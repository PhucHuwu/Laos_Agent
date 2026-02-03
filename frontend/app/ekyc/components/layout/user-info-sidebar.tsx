"use client";

import { useEffect, useState } from "react";
import { ekycProfileApi, type EKYCProfileResponse } from "../../api/ekyc-profile";
import { useUIStore } from "../../stores/ui-store";

interface InfoFieldProps {
    label: string;
    value?: string | null;
}

function InfoField({ label, value }: InfoFieldProps) {
    return (
        <div className="mb-3">
            <p className="text-xs text-muted-foreground mb-0.5">{label}</p>
            <p className="text-sm font-medium text-foreground truncate">{value || "---"}</p>
        </div>
    );
}

export function UserInfoSidebar() {
    const [profile, setProfile] = useState<EKYCProfileResponse | null>(null);
    const [loading, setLoading] = useState(false);
    const { sidebarOpen, closeSidebar } = useUIStore();

    // Fetch eKYC profile from database
    useEffect(() => {
        setLoading(true);
        ekycProfileApi
            .getProfile()
            .then((data) => {
                if (data.success) {
                    setProfile(data);
                }
            })
            .catch((err) => console.error("Failed to fetch eKYC profile:", err))
            .finally(() => setLoading(false));
    }, []);

    const fields = profile?.ocr_data?.fields;
    const isVerified = profile?.is_verified;

    // Build address string
    const addressParts = [];
    if (fields?.address?.childrent?.address_village) {
        addressParts.push(fields.address.childrent.address_village);
    }
    if (fields?.address?.childrent?.address_district) {
        addressParts.push(fields.address.childrent.address_district);
    }
    if (fields?.address?.childrent?.address_province) {
        addressParts.push(fields.address.childrent.address_province);
    }
    const fullAddress = addressParts.length > 0 ? addressParts.join(", ") : fields?.address?.address;

    // Get face image URL from ocr_data.raw_data
    const faceImgUrl = profile?.ocr_data?.raw_data?.img_url;

    const sidebarContent = (
        <>
            {/* Header */}
            <div className="flex items-center justify-between mb-4">
                <h2 className="text-sm font-semibold text-foreground">ຂໍ້ມູນຜູ້ໃຊ້</h2>
                {isVerified && <span className="text-xs px-2 py-0.5 rounded-full bg-green-500/20 text-green-600">ຢັ້ງຢືນແລ້ວ</span>}
            </div>

            {loading ? (
                <div className="flex items-center justify-center py-8">
                    <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary"></div>
                </div>
            ) : (
                <>
                    {/* User Photo */}
                    <div className="mb-4 flex justify-center">
                        {faceImgUrl ? (
                            <img src={faceImgUrl} alt="User Photo" className="w-24 h-24 rounded-lg object-contain border border-border bg-muted" />
                        ) : (
                            <div className="w-24 h-24 rounded-lg bg-muted flex items-center justify-center border border-border">
                                <svg className="w-10 h-10 text-muted-foreground" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path
                                        strokeLinecap="round"
                                        strokeLinejoin="round"
                                        strokeWidth={1.5}
                                        d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                                    />
                                </svg>
                            </div>
                        )}
                    </div>

                    <div className="border-t border-border pt-4">
                        <InfoField label="ເລກບັດປະຈຳຕົວ" value={fields?.id_number} />
                        <InfoField label="ຊື່ ແລະ ນາມສະກຸນ" value={fields?.fullname} />
                        <InfoField label="ວັນເດືອນປີເກີດ" value={fields?.dob} />
                        <InfoField label="ສັນຊາດ" value={fields?.nationality} />
                        <InfoField label="ເຊື້ອຊາດ" value={fields?.ethnicity} />
                        <InfoField label="ທີ່ຢູ່" value={fullAddress} />
                        <InfoField label="ວັນທີອອກບັດ" value={fields?.issue_date} />
                        <InfoField label="ວັນໝົດອາຍຸ" value={fields?.expiry_date} />
                    </div>

                    {/* Verification Score */}
                    {profile?.face_match_score && (
                        <div className="mt-4 pt-4 border-t border-border">
                            <div className="flex items-center justify-between">
                                <span className="text-xs text-muted-foreground">ຄະແນນການຈັບຄູ່ໃບໜ້າ</span>
                                <span className="text-sm font-medium text-foreground">{(profile.face_match_score * 100).toFixed(1)}%</span>
                            </div>
                        </div>
                    )}
                </>
            )}
        </>
    );

    return (
        <>
            {/* Desktop Sidebar */}
            <aside className="w-72 shrink-0 border-r border-border bg-card p-4 overflow-y-auto hidden md:block">{sidebarContent}</aside>

            {/* Mobile Sidebar Overlay */}
            {sidebarOpen && (
                <div className="fixed inset-0 z-50 md:hidden">
                    {/* Backdrop */}
                    <div className="absolute inset-0 bg-black/50 transition-opacity" onClick={closeSidebar} />
                    {/* Sidebar Panel */}
                    <aside className="absolute left-0 top-0 bottom-0 w-72 bg-card p-4 overflow-y-auto shadow-xl animate-in slide-in-from-left duration-200">
                        {/* Close button */}
                        <button onClick={closeSidebar} className="absolute top-4 right-4 p-1 rounded-lg hover:bg-muted transition-colors z-10">
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                            </svg>
                        </button>
                        {/* Content with top padding to avoid close button */}
                        <div className="pt-8">{sidebarContent}</div>
                    </aside>
                </div>
            )}
        </>
    );
}
