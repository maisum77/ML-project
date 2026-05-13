"use client";

import { useState, useEffect } from "react";
import { getFeed } from "../lib/api";
import { ArrowUp, MessageSquare } from "lucide-react";

export default function LiveFeed({ fullView = false }: { fullView?: boolean }) {
  const [posts, setPosts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchFeed = async () => {
      try {
        const data = await getFeed({ limit: fullView ? 50 : 10 });
        setPosts(data.posts || []);
      } catch (err) {
        console.error("Failed to fetch feed:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchFeed();
    const interval = setInterval(fetchFeed, 30000);
    return () => clearInterval(interval);
  }, [fullView]);

  if (loading) return <div className="font-mono text-xs uppercase tracking-widest text-neutral-500 py-4">Loading live feed...</div>;

  return (
    <div>
      <div className={`space-y-0 ${fullView ? "max-h-none" : "max-h-[400px]"} overflow-y-auto scrollbar-hide`}>
        {posts.length === 0 ? (
          <p className="font-body text-neutral-500 text-sm">No posts in feed</p>
        ) : (
          posts.map((post) => (
            <div key={post.id} className="border-b border-ink py-3 group hover:bg-neutral-100 transition-colors duration-200 px-2 -mx-2">
              <div className="flex justify-between items-start gap-4">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="font-sans text-xs uppercase tracking-widest font-semibold text-ink">
                      {post.source}
                    </span>
                    {post.subreddit || post.hashtags?.[0] ? (
                      <span className="font-mono text-[10px] text-neutral-400">
                        {post.subreddit || `#${post.hashtags?.[0]}`}
                      </span>
                    ) : null}
                  </div>
                  {post.title && (
                    <h3 className="font-serif font-bold text-sm leading-tight group-hover:text-editorial-red transition-colors duration-200">
                      {post.title}
                    </h3>
                  )}
                  <p className="font-body text-neutral-600 text-sm truncate mt-0.5">{post.text}</p>
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
          ))
        )}
      </div>
    </div>
  );
}