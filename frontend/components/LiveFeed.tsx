"use client";

import { useState, useEffect } from "react";
import { getFeed } from "../lib/api";

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

  if (loading) return <div className="card">Loading live feed...</div>;

  return (
    <div className="card">
      <h2 className="text-xl font-semibold mb-4">Live Feed</h2>
      <div className="space-y-3 max-h-96 overflow-y-auto">
        {posts.length === 0 ? (
          <p className="text-gray-500">No posts in feed</p>
        ) : (
          posts.map((post) => (
            <div key={post.id} className="border-b pb-2">
              <div className="flex justify-between text-sm">
                <span className={`font-medium ${post.source === "reddit" ? "text-orange-600" : "text-blue-600"}`}>
                  {post.source}
                </span>
                <span className="text-gray-400">
                  {post.subreddit || post.hashtags?.[0] || ""}
                </span>
              </div>
              {post.title && <p className="font-medium mt-1">{post.title}</p>}
              <p className="text-gray-600 text-sm truncate">{post.text}</p>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
