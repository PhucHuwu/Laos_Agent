"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuthStore } from "../ekyc/stores/auth-store";

export default function LoginPage() {
    const router = useRouter();
    const { login, isLoading, error, clearError } = useAuthStore();

    const [phone, setPhone] = useState("");
    const [password, setPassword] = useState("");

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        clearError();

        const success = await login(phone, password);
        if (success) {
            router.push("/");
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-background">
            <div className="w-full max-w-md p-8 space-y-6 bg-card rounded-xl shadow-lg border border-border">
                <div className="text-center">
                    <h1 className="text-2xl font-bold text-foreground">ເຂົ້າສູ່ລະບົບ</h1>
                    <p className="text-muted-foreground mt-2">ລະບົບຢັ້ງຢືນຕົວຕົນທາງເອເລັກໂຕຣນິກ</p>
                </div>

                <form onSubmit={handleSubmit} className="space-y-4">
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

                    {error && <div className="p-3 rounded-lg bg-destructive/10 text-destructive text-sm">{error}</div>}

                    <button
                        type="submit"
                        disabled={isLoading}
                        className="w-full py-2 px-4 bg-primary text-primary-foreground rounded-lg font-medium hover:opacity-90 disabled:opacity-50 transition-opacity"
                    >
                        {isLoading ? "ກຳລັງປະມວນຜົນ..." : "ເຂົ້າສູ່ລະບົບ"}
                    </button>
                </form>

                <div className="text-center text-sm text-muted-foreground">
                    ຍັງບໍ່ມີບັນຊີບໍ?{" "}
                    <Link href="/register" className="text-primary hover:underline">
                        ລົງທະບຽນເລີຍ
                    </Link>
                </div>
            </div>
        </div>
    );
}
