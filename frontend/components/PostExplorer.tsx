"use client";

import { useState, useEffect } from "react";
import { getFeed } from "../lib/api";
import { ArrowUp, MessageSquare, Search } from "lucide-react";

export default function PostExplorer({ fullView = false }: { fullView?: boolean }) {
  const [posts, setPosts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    platform: "",
    sentiment: "",
    limit: 50,
  });

  useEffect(() => {
    const fetchPosts = async () => {
      try {
        const data = await getFeed(filters);
        setPosts(data.posts || []);
      } catch (err) {
        console.error("Failed to fetch posts:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchPosts();
  }, [filters]);

  if (loading) return <div className="font-mono text-xs uppercase tracking-widest text-neutral-500 py-4">Loading posts...</div>;

  return (
    <div className="space-y-6">
      <div className="border border-ink p-6 bg-newsprint">
        <div className="flex flex-col md:flex-row gap-3 mb-6">
          <select
            value={filters.platform}
            onChange={(e) => setFilters({ ...filters, platform: e.target.value })}
            className="newsprint-input flex-1"
            style={{ borderRadius: 0 }}
          >
            <option value="">All Platforms</option>
            <option value="reddit">Reddit</option>
            <option value="twitter">Twitter</option>
          </select>

          <select
            value={filters.sentiment}
            onChange={(e) => setFilters({ ...filters, sentiment: e.target.value })}
            className="newsprint-input flex-1"
            style={{ borderRadius: 0 }}
          >
            <option value="">All Sentiments</option>
            <option value="positive">Positive</option>
            <option value="neutral">Neutral</option>
            <option value="negative">Negative</option>
          </select>
        </div>

        {posts.length === 0 ? (
          <p className="font-body text-neutral-500 text-sm text-center py-12 font-mono text-xs uppercase tracking-widest">
            No posts found
          </p>
        ) : (
          <div className="divide-y divide-ink">
            {posts.map((post) => (
              <div key={post.id} className="py-4 group hover:bg-neutral-100 transition-colors duration-200 px-3 -mx-3">
                <div className="flex justify-between items-start gap-4">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="font-sans text-xs uppercase tracking-widest font-semibold border border-ink px-2 py-0.5">
                        {post.source}
                      </span>
                      {post.sentiment && (
                        <span className={`font-mono text-[10px] uppercase tracking-widest px-2 py-0.5 border ${
                          post.sentiment.label === "positive" ? "border-ink text-ink" :
                          post.sentiment.label === "negative" ? "bg-editorial-red text-newsprint border-editorial-red" :
                          "border-newsprint-muted text-neutral-500"
                        }`}>
                          {post.sentiment.label} {post.sentiment.score != null && `(${(post.sentiment.score * 100).toFixed(0)}%)`}
                        </span>
                      )}
                    </div>
                    {post.title && (
                      <h3 className="font-serif font-bold text-lg leading-tight group-hover:text-editorial-red transition-colors duration-200">
                        {post.title}
                      </h3>
                    )}
                    <p className="font-body text-neutral-600 text-sm mt-1 line-clamp-3">{post.text}</p>
                  </div>
                  <div className="text-right font-mono text-xs text-neutral-400 shrink-0 space-y-1">
                    {post.upvotes > 0 && (
                      <div className="flex items-center gap-1 justify-end">
                        <ArrowUp className="h-3 w-3" strokeWidth={1.5} />
                        {post.upvotes}
                      </div>
                    )}
                    {post.comments_count > 0 && (
                      <div className="flex items-center gap-1 justify-end">
                        <MessageSquare className="h-3 w-3" strokeWidth={1.5} />
                        {post.comments_count}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}