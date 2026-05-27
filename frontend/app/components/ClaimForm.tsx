"use client";
import { useState } from "react";
import { Search, Loader2 } from "lucide-react";

interface Props {
  onSubmit: (claim: string) => void;
  loading: boolean;
}

export default function ClaimForm({ onSubmit, loading }: Props) {
  const [claim, setClaim] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (claim.trim().length >= 10) onSubmit(claim.trim());
  };

  return (
    <form onSubmit={handleSubmit} className="w-full">
      <div className="flex flex-col gap-3">
        <textarea
          value={claim}
          onChange={(e) => setClaim(e.target.value)}
          placeholder="Enter a news claim, headline, or statement to verify..."
          className="w-full p-4 rounded-xl border border-gray-200 bg-white shadow-sm
                     text-gray-800 placeholder-gray-400 resize-none h-32
                     focus:outline-none focus:ring-2 focus:ring-blue-500"
          disabled={loading}
        />
        <button
          type="submit"
          disabled={loading || claim.trim().length < 10}
          className="flex items-center justify-center gap-2 px-6 py-3 rounded-xl
                     bg-blue-600 hover:bg-blue-700 text-white font-semibold
                     disabled:opacity-50 disabled:cursor-not-allowed transition-all"
        >
          {loading ? (
            <><Loader2 className="animate-spin w-4 h-4" /> Verifying...</>
          ) : (
            <><Search className="w-4 h-4" /> Verify Claim</>
          )}
        </button>
      </div>
    </form>
  );
}