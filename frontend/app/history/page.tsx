"use client";
import { useEffect, useState } from "react";

interface HistoryRecord {
  id: string;
  claim: string;
  credibility: string;
  summary: string;
  confidence: number;
  created_at: string;
}

const credibilityColors: Record<string, string> = {
  true: "bg-green-100 text-green-800",
  false: "bg-red-100 text-red-800",
  misleading: "bg-yellow-100 text-yellow-800",
  unverified: "bg-gray-100 text-gray-800",
};

export default function HistoryPage() {
  const [records, setRecords] = useState<HistoryRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch(`${process.env.NEXT_PUBLIC_API_URL}/agent/history?limit=50`)
      .then((r) => r.json())
      .then((data) => {
        setRecords(data.records || []);
        setLoading(false);
      })
      .catch((e) => {
        setError("Failed to load history");
        setLoading(false);
      });
  }, []);

  return (
    <main className="min-h-screen bg-gray-50 py-10 px-4">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Verification History
        </h1>
        <p className="text-gray-500 mb-8">
          All past verifications stored in the database
        </p>

        {loading && (
          <div className="text-center py-20 text-gray-400">Loading...</div>
        )}

        {error && (
          <div className="text-center py-20 text-red-500">{error}</div>
        )}

        {!loading && records.length === 0 && (
          <div className="text-center py-20 text-gray-400">
            No verifications yet. Go verify a claim!
          </div>
        )}

        <div className="space-y-4">
          {records.map((r) => (
            <div
              key={r.id}
              className="bg-white rounded-xl shadow-sm border border-gray-200 p-6"
            >
              <div className="flex items-start justify-between gap-4">
                <p className="text-gray-900 font-medium flex-1">{r.claim}</p>
                <span
                  className={`text-xs font-semibold px-3 py-1 rounded-full capitalize whitespace-nowrap ${
                    credibilityColors[r.credibility] || credibilityColors.unverified
                  }`}
                >
                  {r.credibility}
                </span>
              </div>
              <p className="text-gray-600 text-sm mt-2">{r.summary}</p>
              <div className="flex items-center gap-4 mt-3 text-xs text-gray-400">
                <span>Confidence: {Math.round(r.confidence * 100)}%</span>
                <span>
                  {new Date(r.created_at).toLocaleString()}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </main>
  );
}