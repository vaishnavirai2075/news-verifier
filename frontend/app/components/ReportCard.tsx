import Badge from "./Badge";
import SourceList from "./SourceList";
import { VerificationReport } from "../lib/api";
import { ShieldCheck, AlertTriangle, Database, Brain, Globe } from "lucide-react";

interface Props {
  report: VerificationReport;
  cacheHit: boolean;
}

const biasColors: Record<string, string> = {
  political_left: "bg-blue-100 text-blue-700",
  political_right: "bg-red-100 text-red-700",
  emotional: "bg-orange-100 text-orange-700",
  sensational: "bg-yellow-100 text-yellow-700",
  neutral: "bg-green-100 text-green-700",
};

export default function ReportCard({ report, cacheHit }: Props) {
  const bias = (report as any).bias_analysis;
  const diversity = (report as any).source_diversity;

  return (
    <div className="w-full bg-white rounded-2xl shadow-md border border-gray-100 p-6 mt-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <ShieldCheck className="text-blue-500 w-5 h-5" />
          <h2 className="font-bold text-gray-800 text-lg">Verification Report</h2>
        </div>
        <div className="flex items-center gap-2">
          {cacheHit && (
            <span className="flex items-center gap-1 text-xs bg-purple-100 text-purple-700 px-2 py-1 rounded-full">
              <Database className="w-3 h-3" /> Cached
            </span>
          )}
          <Badge verdict={report.verdict} />
        </div>
      </div>

      {/* Claim */}
      <p className="text-gray-600 text-sm italic mb-4">"{report.claim}"</p>

      {/* Confidence */}
      <div className="mb-4">
        <div className="flex justify-between text-xs text-gray-500 mb-1">
          <span>Confidence Score</span>
          <span>{(report.confidence_score * 100).toFixed(0)}%</span>
        </div>
        <div className="w-full bg-gray-100 rounded-full h-2">
          <div
            className="bg-blue-500 h-2 rounded-full transition-all"
            style={{ width: `${report.confidence_score * 100}%` }}
          />
        </div>
      </div>

      {/* Summary */}
      <div className="mb-3">
        <h3 className="font-semibold text-gray-700 mb-1">Summary</h3>
        <p className="text-gray-600 text-sm">{report.summary}</p>
      </div>

      {/* Reasoning */}
      <div className="mb-3">
        <h3 className="font-semibold text-gray-700 mb-1">Reasoning</h3>
        <p className="text-gray-600 text-sm">{report.reasoning}</p>
      </div>

      {/* Stats Row */}
      <div className="grid grid-cols-3 gap-3 my-4">
        {[
          { label: "Total Sources", value: report.total_sources },
          { label: "High Credibility", value: report.high_credibility_sources },
          { label: "Consensus", value: report.source_consensus },
        ].map((stat) => (
          <div key={stat.label} className="bg-gray-50 rounded-xl p-3 text-center">
            <p className="text-xl font-bold text-blue-600">{stat.value}</p>
            <p className="text-xs text-gray-500">{stat.label}</p>
          </div>
        ))}
      </div>

      {/* Bias Analysis */}
      {bias && (
        <div className="mb-4 p-3 bg-gray-50 border border-gray-200 rounded-xl">
          <div className="flex items-center gap-1 mb-2">
            <Brain className="w-4 h-4 text-gray-600" />
            <h3 className="font-semibold text-gray-700 text-sm">Bias Analysis</h3>
          </div>
          <div className="flex items-center gap-2 mb-2">
            <span className={`text-xs font-semibold px-2 py-1 rounded-full capitalize ${biasColors[bias.bias_type] || "bg-gray-100 text-gray-700"}`}>
              {bias.bias_type.replace("_", " ")}
            </span>
            <span className="text-xs text-gray-500">
              Score: {(bias.bias_score * 100).toFixed(0)}%
            </span>
          </div>
          <p className="text-xs text-gray-600 mb-1">{bias.explanation}</p>
          {bias.bias_indicators?.length > 0 && (
            <div className="flex flex-wrap gap-1 mt-1">
              {bias.bias_indicators.map((indicator: string, i: number) => (
                <span key={i} className="text-xs bg-gray-200 text-gray-600 px-2 py-0.5 rounded-full">
                  {indicator}
                </span>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Source Diversity */}
      {diversity && (
        <div className="mb-4 p-3 bg-gray-50 border border-gray-200 rounded-xl">
          <div className="flex items-center gap-1 mb-2">
            <Globe className="w-4 h-4 text-gray-600" />
            <h3 className="font-semibold text-gray-700 text-sm">Source Diversity</h3>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2 mb-2">
            <div
              className="bg-green-500 h-2 rounded-full transition-all"
              style={{ width: `${diversity.diversity_score * 100}%` }}
            />
          </div>
          <div className="flex justify-between text-xs text-gray-500 mb-1">
            <span>{diversity.unique_domains} unique domains</span>
            <span>{(diversity.diversity_score * 100).toFixed(0)}% diverse</span>
          </div>
          <p className="text-xs text-gray-600">{diversity.recommendation}</p>
        </div>
      )}

      {/* Contradictions */}
      {report.contradictions?.length > 0 && (
        <div className="mb-4 p-3 bg-yellow-50 border border-yellow-200 rounded-xl">
          <div className="flex items-center gap-1 mb-2">
            <AlertTriangle className="w-4 h-4 text-yellow-600" />
            <h3 className="font-semibold text-yellow-700 text-sm">
              Contradictions Found ({report.contradictions.length})
            </h3>
          </div>
          {report.contradictions.map((c, i) => (
            <div key={i} className="text-xs text-yellow-800 mb-1">
              <strong>{c.source_a}</strong> vs <strong>{c.source_b}</strong>: {c.description}
            </div>
          ))}
        </div>
      )}

      {/* Sources */}
      <SourceList sources={report.sources} />
    </div>
  );
}