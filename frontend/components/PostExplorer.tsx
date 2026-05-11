"use client";

import { useState, useEffect } from "react";
import { getFeed } from "../lib/api";

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

  if (loading) return <div className="card">Loading posts...</div>;

  return (
    <div className={fullView ? "card" : "card"}>
      <h2 className="text-xl font-semibold mb-4">Post Explorer</h2>

      <div className="flex gap-4 mb-4">
        <select
          value={filters.platform}
          onChange={(e) => setFilters({ ...filters, platform: e.target.value })}
          className="border rounded px-3 py-2"
        >
          <option value="">All Platforms</option>
          <option value="reddit">Reddit</option>
          <option value="twitter">Twitter</option>
        </select>

        <select
          value={filters.sentiment}
          onChange={(e) => setFilters({ ...filters, sentiment: e.target.value })}
          className="border rounded px-3 py-2"
        >
          <option value="">All Sentiments</option>
          <option value="positive">Positive</option>
          <option value="neutral">Neutral</option>
          <option value="negative">Negative</option>
        </select>
      </div>

      <div className="space-y-4">
        {posts.length === 0 ? (
          <p className="text-gray-500">No posts found</p>
        ) : (
          posts.map((post) => (
            <div key={post.id} className="border rounded p-4">
              <div className="flex justify-between items-start">
                <div>
                  <span className={`badge ${post.source === "reddit" ? "bg-orange-100 text-orange-800" : "bg-blue-100 text-blue-800"}`}>
                    {post.source}
                  </span>
                  {post.title && <h3 className="font-medium mt-2">{post.title}</h3>}
                  <p className="text-gray-600 text-sm mt-1 line-clamp-3">{post.text}</p>
                </div>
                <div className="text-right text-sm text-gray-500">
                  <div>{post.upvotes || 0} upvotes</div>
                  <div>{post.comments_count || 0} comments</div>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
