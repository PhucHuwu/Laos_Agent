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
            setLocalError("Mật khẩu xác nhận không khớp");
            return;
        }

        // Validate password length
        if (password.length < 6) {
            setLocalError("Mật khẩu phải có ít nhất 6 ký tự");
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
                    <h1 className="text-2xl font-bold text-foreground">Đăng Ký</h1>
                    <p className="text-muted-foreground mt-2">Tạo tài khoản mới</p>
                </div>

                <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                        <label htmlFor="fullName" className="block text-sm font-medium text-foreground mb-1">
                            Họ và tên
                        </label>
                        <input
                            id="fullName"
                            type="text"
                            value={fullName}
                            onChange={(e) => setFullName(e.target.value)}
                            placeholder="Nguyen Van A"
                            className="w-full px-4 py-2 rounded-lg border border-input bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
                        />
                    </div>

                    <div>
                        <label htmlFor="phone" className="block text-sm font-medium text-foreground mb-1">
                            Số điện thoại
                        </label>
                        <input
                            id="phone"
                            type="tel"
                            value={phone}
                            onChange={(e) => setPhone(e.target.value)}
                            placeholder="0901234567"
                            required
                            className="w-full px-4 py-2 rounded-lg border border-input bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
                        />
                    </div>

                    <div>
                        <label htmlFor="password" className="block text-sm font-medium text-foreground mb-1">
                            Mật khẩu
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
                            Xác nhận mật khẩu
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
                        {isLoading ? "Đang xử lý..." : "Đăng ký"}
                    </button>
                </form>

                <div className="text-center text-sm text-muted-foreground">
                    Đã có tài khoản?{" "}
                    <Link href="/login" className="text-primary hover:underline">
                        Đăng nhập
                    </Link>
                </div>
            </div>
        </div>
    );
}
