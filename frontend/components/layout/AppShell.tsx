"use client";

import TopNavbar from "@/components/dashboard/TopNavbar";

interface AppShellProps {
  children: React.ReactNode;
}

export default function AppShell({ children }: AppShellProps) {
  return (
    <div className="min-h-screen bg-[#0B0F17] text-slate-100 flex flex-col antialiased">
      <TopNavbar />
      <main className="flex-1 p-6 md:p-8 max-w-[1750px] w-full mx-auto">
        {children}
      </main>
    </div>
  );
}
