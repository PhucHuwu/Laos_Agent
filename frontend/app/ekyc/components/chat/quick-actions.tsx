"use client";

import { Upload, Camera, HelpCircle } from "lucide-react";

interface QuickActionsProps {
    onAction: (action: string) => void;
    isLoading?: boolean;
}

export function QuickActions({ onAction, isLoading }: QuickActionsProps) {
    const actions = [
        { id: "upload_id", label: "ອັບໂຫລດບັດປະຈຳຕົວ", icon: Upload },
        { id: "start_verification", label: "ເລີ່ມຕົ້ນຢັ້ງຢືນ", icon: Camera },
        { id: "help", label: "ຕ້ອງການຄວາມຊ່ວຍເຫຼືອ?", icon: HelpCircle },
    ];

    return (
        <div className="px-4 pb-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-2 max-w-2xl mx-auto">
                {actions.map((action) => {
                    const IconComponent = action.icon;
                    return (
                        <button
                            key={action.id}
                            onClick={() => onAction(action.id)}
                            disabled={isLoading}
                            className="flex flex-col items-center gap-2 p-4 rounded-lg border border-border hover:bg-muted hover:border-primary/50 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                        >
                            <IconComponent className="w-6 h-6 text-primary" />
                            <span className="text-sm font-medium text-center">{action.label}</span>
                        </button>
                    );
                })}
            </div>
        </div>
    );
}
