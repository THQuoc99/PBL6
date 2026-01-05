//index.tsx
import React from "react";
import dynamic from "next/dynamic";

const AppRouter = dynamic(() => import("../AppRouter"), {
  ssr: false,
  loading: () => <div className="flex items-center justify-center min-h-screen">Loading...</div>
});

export default function Home() {
  return (
    <div>
      <AppRouter />
    </div>
  );
}
