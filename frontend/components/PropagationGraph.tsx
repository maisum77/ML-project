"use client";

interface CascadeNode {
  depth: number;
  post_id: string;
  author: string;
  platform: string;
  text?: string;
  retweets: number;
  upvotes: number;
  authority_score: number;
  author_type: string;
  is_authentic: boolean;
  location?: { name: string; lat: number; lng: number } | null;
}

const getBadgeStyle = (type: string) => {
  if (type === "official") return "bg-ink text-newsprint";
  if (type === "org") return "border border-ink";
  if (type === "journalist") return "border border-ink border-dashed";
  return "bg-newsprint-muted text-neutral-600";
};

const getBadgeLabel = (type: string) => {
  if (type === "official") return "Official";
  if (type === "org") return "Organization";
  if (type === "journalist") return "Journalist";
  return "Public";
};

type PropagationData = {
  origin?: {
    post_id: string;
    author: string;
    platform: string;
    text: string;
    authority_score: number;
    author_type: string;
    is_authentic: boolean;
    reasons: string[];
  };
  chain_length?: number;
  cascade?: CascadeNode[];
  topic?: string;
  total_posts?: number;
  origins?: {
    post_id: string;
    author: string;
    platform: string;
    text: string;
    authority_score: number;
    author_type: string;
    is_authentic: boolean;
    location: { name: string; lat: number; lng: number } | null;
  }[];
  cascades?: {
    origin_id: string;
    origin_author: string | null;
    origin_authority_score?: number;
    origin_is_authentic?: boolean;
    nodes: CascadeNode[];
  }[];
};

export default function PropagationGraph({ data }: { data: PropagationData | null }) {
  if (!data) {
    return (
      <div className="border border-ink p-6 text-center">
        <p className="font-mono text-xs uppercase tracking-widest text-neutral-500">No propagation data available</p>
      </div>
    );
  }

  const origins = data.origins || (data.origin ? [data.origin] : []);
  const cascades = data.cascades || (data.cascade ? [{ origin_id: data.origin?.post_id || "", origin_author: data.origin?.author || null, origin_authority_score: data.origin?.authority_score, origin_is_authentic: data.origin?.is_authentic, nodes: data.cascade }] : []);

  return (
    <div className="space-y-6">
      {data.topic && (
        <div className="border border-ink p-4 flex items-center gap-4">
          <span className="label-uppercase">Topic:</span>
          <span className="font-mono text-lg font-bold">{data.topic}</span>
          <span className="label-uppercase text-neutral-500 ml-auto">{data.total_posts} posts found</span>
        </div>
      )}

      {origins.length > 0 && (
        <div className="border border-ink">
          <div className="p-2 bg-ink text-newsprint label-uppercase text-center">Origin Posts</div>
          {origins.map((origin) => (
            <div key={origin.post_id} className="p-4 border-b border-newsprint-muted last:border-b-0">
              <div className="flex items-center gap-3 mb-2">
                <span className="bg-editorial-red text-newsprint px-2 py-0.5 font-sans text-[10px] uppercase tracking-widest font-bold">
                  Origin
                </span>
                <span className={`px-2 py-0.5 font-sans text-[10px] uppercase tracking-widest ${getBadgeStyle(origin.author_type)}`}>
                  {getBadgeLabel(origin.author_type)}
                </span>
                {origin.is_authentic && (
                  <span className="border border-ink px-2 py-0.5 font-sans text-[10px] uppercase tracking-widest">
                    Authentic
                  </span>
                )}
              </div>
              <p className="font-serif font-bold text-lg">
                @{origin.author} <span className="font-body text-neutral-400 font-normal">on {origin.platform}</span>
              </p>
              <p className="font-body text-neutral-600 text-sm mt-1">{origin.text}</p>
              <div className="font-mono text-xs text-neutral-400 mt-2">
                Authority: {origin.authority_score}/100
              </div>
            </div>
          ))}
        </div>
      )}

      {cascades.map((cascade) => (
        <div key={cascade.origin_id} className="border border-ink">
          <div className="p-4 border-b border-newsprint-muted flex items-center gap-3">
            <span className="label-uppercase">Chain Length</span>
            <span className="font-mono text-lg font-bold">{cascade.nodes.length} hops</span>
            {cascade.origin_author && (
              <span className="label-uppercase text-neutral-400 ml-auto">from @{cascade.origin_author}</span>
            )}
          </div>

          <div className="p-6">
            {cascade.nodes
              .filter((n) => n.depth > 0)
              .map((node, index) => (
                <div key={node.post_id} className="relative pl-8 pb-4 last:pb-0">
                  {index < cascade.nodes.length - 2 && (
                    <div className="absolute left-[11px] top-8 bottom-0 w-0.5 bg-ink" />
                  )}
                  <div className="absolute left-2 top-6 w-4 h-0.5 bg-newsprint-muted" />
                  <div className="absolute left-0 top-4 w-6 h-6 border border-ink bg-newsprint flex items-center justify-center">
                    <span className="font-mono text-[10px] font-bold">{node.depth}</span>
                  </div>

                  <div className="border border-ink p-4 hover:shadow-hard hover:-translate-x-0.5 hover:-translate-y-0.5 transition-all duration-200 bg-newsprint">
                    <div className="flex items-center justify-between mb-1">
                      <div className="flex items-center gap-2">
                        <span className={`px-2 py-0.5 border font-sans text-[10px] uppercase tracking-widest ${getBadgeStyle(node.author_type)}`}>
                          {getBadgeLabel(node.author_type)} {node.authority_score}
                        </span>
                      </div>
                      {node.location && (
                        <span className="font-mono text-[10px] uppercase tracking-widest text-neutral-400">
                          {node.location.name}
                        </span>
                      )}
                    </div>
                    <p className="font-serif font-bold text-sm">
                      @{node.author} <span className="font-body text-neutral-400 font-normal">on {node.platform}</span>
                    </p>
                    {node.text && (
                      <p className="font-body text-neutral-600 text-xs mt-1">{node.text}</p>
                    )}
                    <div className="flex gap-3 mt-2 font-mono text-[10px] text-neutral-400 uppercase tracking-widest">
                      {node.retweets > 0 && <span>{node.retweets} retweets</span>}
                      {node.upvotes > 0 && <span>{node.upvotes} upvotes</span>}
                    </div>
                  </div>
                </div>
              ))}
          </div>
        </div>
      ))}

      {origins.length === 0 && cascades.length === 0 && (
        <div className="border border-ink p-6 text-center">
          <p className="font-mono text-xs uppercase tracking-widest text-neutral-500">No propagation data available</p>
        </div>
      )}
    </div>
  );
}