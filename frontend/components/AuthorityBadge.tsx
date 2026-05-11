"use client";

interface AuthorityBadgeProps {
  author: string;
  authorType: string;
  authorityScore: number;
  isAuthentic: boolean;
  verified: boolean;
  reasons?: string[];
}

export default function AuthorityBadge({
  author,
  authorType,
  authorityScore,
  isAuthentic,
  verified,
  reasons,
}: AuthorityBadgeProps) {
  const getColors = () => {
    if (isAuthentic) return "border-green-400 bg-green-50";
    if (authorityScore >= 50) return "border-yellow-400 bg-yellow-50";
    return "border-gray-300 bg-gray-50";
  };

  const getLabel = () => {
    if (authorType === "official") return "Official Source";
    if (authorType === "org") return "Organization";
    if (authorType === "journalist") return "Journalist";
    return "Public";
  };

  const getIcon = () => {
    if (isAuthentic) return "check-badge";
    if (verified) return "verified";
    if (authorityScore >= 60) return "info";
    return "person";
  };

  return (
    <div className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-full border ${getColors()} text-xs`}>
      {isAuthentic ? (
        <span className="text-green-600 font-bold">Authentic</span>
      ) : (
        <span className="text-gray-500">{getLabel()}</span>
      )}
      <span className="text-gray-400">|</span>
      <span className="font-medium text-gray-700">{authorityScore}/100</span>
      {reasons && reasons.length > 0 && (
        <span className="text-gray-400 cursor-help" title={reasons.join(", ")}>
          ?
        </span>
      )}
    </div>
  );
}
