interface BadgeProps {
  verdict: string;
}

const config: Record<string, { label: string; classes: string }> = {
  true:        { label: "✅ True",        classes: "bg-green-100 text-green-800 border-green-300" },
  false:       { label: "❌ False",       classes: "bg-red-100 text-red-800 border-red-300" },
  misleading:  { label: "⚠️ Misleading",  classes: "bg-yellow-100 text-yellow-800 border-yellow-300" },
  unverified:  { label: "❓ Unverified",  classes: "bg-gray-100 text-gray-700 border-gray-300" },
};

export default function Badge({ verdict }: BadgeProps) {
  const style = config[verdict] ?? config["unverified"];
  return (
    <span className={`px-3 py-1 rounded-full text-sm font-semibold border ${style.classes}`}>
      {style.label}
    </span>
  );
}