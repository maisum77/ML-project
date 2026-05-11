"use client";

interface CascadeNode {
  depth: number;
  post_id: string;
  author: string;
  platform: string;
  text: string;
  retweets: number;
  upvotes: number;
  authority_score: number;
  author_type: string;
  is_authentic: boolean;
  location?: { name: string; lat: number; lng: number } | null;
}

interface PropagationData {
  origin: {
    post_id: string;
    author: string;
    platform: string;
    text: string;
    authority_score: number;
    author_type: string;
    is_authentic: boolean;
    reasons: string[];
  };
  chain_length: number;
  cascade: CascadeNode[];
}

export default function PropagationGraph({ data }: { data: PropagationData | null }) {
  if (!data) {
    return (
      <div className="bg-white rounded-lg shadow p-6 text-center">
        <p className="text-gray-400">No propagation data available</p>
      </div>
    );
  }

  const getBadgeStyle = (type: string, score: number) => {
    if (type === "official") return "bg-green-100 text-green-800 border-green-300";
    if (type === "org") return "bg-blue-100 text-blue-800 border-blue-300";
    if (type === "journalist") return "bg-purple-100 text-purple-800 border-purple-300";
    return "bg-gray-100 text-gray-600 border-gray-300";
  };

  const getBadgeLabel = (type: string) => {
    if (type === "official") return "Official";
    if (type === "org") return "Organization";
    if (type === "journalist") return "Journalist";
    return "Public";
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">Propagation Chain</h2>

      {/* Origin */}
      <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <span className="text-sm font-bold text-green-700">ORIGIN</span>
            <span className={`px-2 py-0.5 rounded-full text-xs font-medium border ${getBadgeStyle(data.origin.author_type, data.origin.authority_score)}`}>
              {getBadgeLabel(data.origin.author_type)}
            </span>
            {data.origin.is_authentic && (
              <span className="px-2 py-0.5 rounded-full text-xs font-medium bg-green-600 text-white">
                Authentic
              </span>
            )}
          </div>
          <span className="text-xs text-gray-500">
            Score: {data.origin.authority_score}/100
          </span>
        </div>
        <p className="text-sm font-medium text-gray-900">
          @{data.origin.author} <span className="text-gray-400">on</span> {data.origin.platform}
        </p>
        <p className="text-sm text-gray-600 mt-1">{data.origin.text}</p>
        {data.origin.reasons.length > 0 && (
          <div className="mt-2 flex flex-wrap gap-1">
            {data.origin.reasons.map((r, i) => (
              <span key={i} className="text-xs text-green-600 bg-green-50 px-2 py-0.5 rounded">
                {r}
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Chain Length */}
      <div className="mb-4 flex items-center gap-2">
        <span className="text-sm text-gray-500">Chain length:</span>
        <span className="text-sm font-semibold text-gray-700">{data.chain_length} hops</span>
      </div>

      {/* Cascade Nodes */}
      {data.cascade
        .filter((n) => n.depth > 0)
        .map((node, index) => (
          <div key={node.post_id} className="relative pl-8 pb-4">
            {/* Vertical line */}
            {index < data.cascade.length - 2 && (
              <div className="absolute left-4 top-8 bottom-0 w-0.5 bg-blue-200" />
            )}
            {/* Horizontal connector */}
            <div className="absolute left-4 top-6 w-4 h-0.5 bg-blue-200" />

            <div className="p-3 bg-gray-50 border border-gray-200 rounded-lg">
              <div className="flex items-center justify-between mb-1">
                <div className="flex items-center gap-2">
                  <span className="text-xs text-gray-400">Depth {node.depth}</span>
                  <span className={`px-2 py-0.5 rounded-full text-xs font-medium border ${getBadgeStyle(node.author_type, node.authority_score)}`}>
                    {getBadgeLabel(node.author_type)} {node.authority_score}
                  </span>
                </div>
                {node.location && (
                  <span className="text-xs text-blue-500">
                    {node.location.name}
                  </span>
                )}
              </div>
              <p className="text-sm font-medium text-gray-800">
                @{node.author} <span className="text-gray-400">on</span> {node.platform}
              </p>
              <p className="text-xs text-gray-500 mt-1">{node.text}</p>
              <div className="flex gap-3 mt-2 text-xs text-gray-400">
                {node.retweets > 0 && <span>{node.retweets} retweets</span>}
                {node.upvotes > 0 && <span>{node.upvotes} upvotes</span>}
              </div>
            </div>
          </div>
        ))}
    </div>
  );
}
