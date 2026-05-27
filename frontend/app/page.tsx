"use client";
import { useState } from "react";
import ClaimForm from "./components/ClaimForm";
import ReportCard from "./components/ReportCard";
import { verifyClaim, AgentResponse } from "./lib/api";
import { Newspaper } from "lucide-react";
import Link from "next/link";

export default function Home() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AgentResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleVerify = async (claim: string) => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await verifyClaim(claim);
      setResult(data);
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Verification failed. Is the backend running?");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-gray-50">
      <div className="max-w-2xl mx-auto px-4 py-12">

        {/* Header */}
        <div className="text-center mb-10">
          <div className="flex items-center justify-center gap-2 mb-3">
            <Newspaper className="text-blue-600 w-8 h-8" />
            <h1 className="text-3xl font-bold text-gray-900">News Verifier</h1>
          </div>
          <p className="text-gray-500 text-sm">
            Autonomous AI-powered fact-checking with multi-agent workflows
          </p>
          <Link href="/history" className="text-blue-500 hover:underline text-sm mt-2 inline-block">
            View Verification History →
          </Link>
        </div>

        {/* Form */}
        <ClaimForm onSubmit={handleVerify} loading={loading} />

        {/* Error */}
        {error && (
          <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-xl text-red-700 text-sm">
            {error}
          </div>
        )}

        {/* Report */}
        {result?.report && (
          <ReportCard report={result.report} cacheHit={result.cache_hit} />
        )}
      </div>
    </main>
  );
}
