"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuthStore } from "../ekyc/stores/auth-store";

export default function RegisterPage() {
    const router = useRouter();
    const { register, isLoading, error, clearError } = useAuthStore();

    const [phone, setPhone] = useState("");
    const [password, setPassword] = useState("");
    const [confirmPassword, setConfirmPassword] = useState("");
    const [fullName, setFullName] = useState("");
    const [localError, setLocalError] = useState("");

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        clearError();
        setLocalError("");

        // Validate password match
        if (password !== confirmPassword) {
            setLocalError("ລະຫັດຜ່ານຢືນຢັນບໍ່ກົງກັນ");
            return;
        }

        // Validate password length
        if (password.length < 6) {
            setLocalError("ລະຫັດຜ່ານຕ້ອງມີຢ່າງໜ້ອຍ 6 ຕົວອັກສອນ");
            return;
        }

        const success = await register(phone, password, fullName || undefined);
        if (success) {
            router.push("/");
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-background">
            <div className="w-full max-w-md p-8 space-y-6 bg-card rounded-xl shadow-lg border border-border">
                <div className="text-center">
                    <h1 className="text-2xl font-bold text-foreground">ລົງທະບຽນ</h1>
                    <p className="text-muted-foreground mt-2">ສ້າງບັນຊີໃໝ່</p>
                </div>

                <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                        <label htmlFor="fullName" className="block text-sm font-medium text-foreground mb-1">
                            ຊື່ ແລະ ນາມສະກຸນ
                        </label>
                        <input
                            id="fullName"
                            type="text"
                            value={fullName}
                            onChange={(e) => setFullName(e.target.value)}
                            placeholder="Somsak Vongsa"
                            className="w-full px-4 py-2 rounded-lg border border-input bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
                        />
                    </div>

                    <div>
                        <label htmlFor="phone" className="block text-sm font-medium text-foreground mb-1">
                            ເບີໂທລະສັບ
                        </label>
                        <input
                            id="phone"
                            type="tel"
                            value={phone}
                            onChange={(e) => setPhone(e.target.value)}
                            placeholder="020 12345678"
                            required
                            className="w-full px-4 py-2 rounded-lg border border-input bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
                        />
                    </div>

                    <div>
                        <label htmlFor="password" className="block text-sm font-medium text-foreground mb-1">
                            ລະຫັດຜ່ານ
                        </label>
                        <input
                            id="password"
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            placeholder="******"
                            required
                            className="w-full px-4 py-2 rounded-lg border border-input bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
                        />
                    </div>

                    <div>
                        <label htmlFor="confirmPassword" className="block text-sm font-medium text-foreground mb-1">
                            ຢືນຢັນລະຫັດຜ່ານ
                        </label>
                        <input
                            id="confirmPassword"
                            type="password"
                            value={confirmPassword}
                            onChange={(e) => setConfirmPassword(e.target.value)}
                            placeholder="******"
                            required
                            className="w-full px-4 py-2 rounded-lg border border-input bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
                        />
                    </div>

                    {(error || localError) && <div className="p-3 rounded-lg bg-destructive/10 text-destructive text-sm">{localError || error}</div>}

                    <button
                        type="submit"
                        disabled={isLoading}
                        className="w-full py-2 px-4 bg-primary text-primary-foreground rounded-lg font-medium hover:opacity-90 disabled:opacity-50 transition-opacity"
                    >
                        {isLoading ? "ກຳລັງປະມວນຜົນ..." : "ລົງທະບຽນ"}
                    </button>
                </form>

                <div className="text-center text-sm text-muted-foreground">
                    ມີບັນຊີຢູ່ແລ້ວບໍ?{" "}
                    <Link href="/login" className="text-primary hover:underline">
                        ເຂົ້າສູ່ລະບົບ
                    </Link>
                </div>
            </div>
        </div>
    );
}
