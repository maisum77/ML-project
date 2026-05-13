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
  const getBadgeStyle = () => {
    if (isAuthentic) return "bg-ink text-newsprint border-ink";
    if (authorityScore >= 50) return "border-2 border-ink";
    return "border border-newsprint-muted text-neutral-600";
  };

  const getLabel = () => {
    if (authorType === "official") return "Official";
    if (authorType === "org") return "Organization";
    if (authorType === "journalist") return "Journalist";
    return "Public";
  };

  return (
    <div className={`inline-flex items-center gap-2 px-3 py-1.5 border ${getBadgeStyle()} font-sans text-[10px] uppercase tracking-widest font-semibold`}>
      {isAuthentic ? (
        <span className="text-newsprint font-bold">Authentic</span>
      ) : (
        <span>{getLabel()}</span>
      )}
      <span className="text-neutral-400">|</span>
      <span className="font-mono font-bold">{authorityScore}/100</span>
      {reasons && reasons.length > 0 && (
        <span className="text-neutral-400 cursor-help" title={reasons.join(", ")}>
          ?
        </span>
      )}
    </div>
  );
}