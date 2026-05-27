interface Source {
  title: string;
  url: string;
  content: string;
  credibility_score: number;
  domain_tier: string;
}

const tierColors: Record<string, string> = {
  high: "bg-green-100 text-green-700",
  medium: "bg-yellow-100 text-yellow-700",
  low: "bg-red-100 text-red-700",
};

export default function SourceList({
  sources,
}: {
  sources: Source[];
}) {
  if (!sources?.length) return null;

  return (
    <div className="mt-4">
      <h3 className="font-semibold text-gray-700 mb-2">
        Sources ({sources.length})
      </h3>

      <div className="flex flex-col gap-2">
        {sources.map((s, i) => (
          <div
            key={i}
            className="p-3 bg-gray-50 rounded-lg border border-gray-100"
          >
            <div className="flex items-center justify-between mb-1">
              <a
                href={s.url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 hover:underline text-sm font-medium truncate max-w-xs"
              >
                {s.title || s.url}
              </a>

              <span
                className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                  tierColors[s.domain_tier] ?? tierColors.low
                }`}
              >
                {s.domain_tier} •{" "}
                {(s.credibility_score * 100).toFixed(0)}%
              </span>
            </div>

            <p className="text-gray-500 text-xs line-clamp-2">
              {s.content}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}