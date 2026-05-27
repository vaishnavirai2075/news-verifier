import axios from "axios";

const API = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
});

export interface VerificationReport {
  claim: string;
  verdict: "true" | "false" | "misleading" | "unverified";
  confidence_score: number;
  summary: string;
  reasoning: string;
  contradictions: {
    source_a: string;
    source_b: string;
    description: string;
    severity: string;
  }[];
  sources: {
    title: string;
    url: string;
    content: string;
    source: string;
    credibility_score: number;
    domain_tier: string;
  }[];
  source_consensus: string;
  total_sources: number;
  high_credibility_sources: number;
  report_status: string;
}

export interface AgentResponse {
  workflow_status: string;
  cache_hit: boolean;
  steps_completed: string;
  report: VerificationReport;
}

export async function verifyClaim(claim: string): Promise<AgentResponse> {
  const res = await API.post("/agent/verify", { claim });
  // Backend returns report directly, wrap it to match AgentResponse shape
  return {
    workflow_status: "completed",
    cache_hit: false,
    steps_completed: "all",
    report: res.data,
  };
}

export async function getHistory(): Promise<{ total: number; claims: any[] }> {
  const res = await API.get("/agent/history");
  return res.data;
}