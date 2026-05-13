"use client";

import { useState } from "react";
import { useAuth } from "../lib/auth";

export default function AuthForm() {
  const { login, register } = useAuth();
  const [isLogin, setIsLogin] = useState(true);
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    let success: boolean;
    if (isLogin) {
      success = await login(username, password);
    } else {
      success = await register(username, email, password);
    }

    if (!success) {
      setError(isLogin ? "Invalid username or password" : "Registration failed. Username may already exist.");
    }
    setLoading(false);
  };

  return (
    <div className="max-w-lg mx-auto">
      <div className="border border-ink p-8 bg-newsprint">
        <h2 className="font-serif text-3xl font-black text-center mb-2">
          {isLogin ? "Sign In" : "Create Account"}
        </h2>
        <p className="font-body text-neutral-500 text-sm text-center mb-8">
          {isLogin
            ? "Sign in to save analyses and set keyword alerts"
            : "Join SocialPulse AI to track misinformation"}
        </p>

        {error && (
          <div className="border-2 border-editorial-red p-4 mb-6 font-mono text-xs text-editorial-red uppercase tracking-widest">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="label-uppercase block mb-2">Username</label>
            <input
              type="text"
              required
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full newsprint-input"
              style={{ borderRadius: 0 }}
              placeholder="Enter your username"
            />
          </div>

          {!isLogin && (
            <div>
              <label className="label-uppercase block mb-2">Email</label>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full newsprint-input"
                style={{ borderRadius: 0 }}
                placeholder="you@example.com"
              />
            </div>
          )}

          <div>
            <label className="label-uppercase block mb-2">Password</label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full newsprint-input"
              style={{ borderRadius: 0 }}
              placeholder="Min 6 characters"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? "Please wait..." : isLogin ? "Sign In" : "Create Account"}
          </button>
        </form>

        <div className="mt-6 text-center font-sans text-xs uppercase tracking-widest text-neutral-500">
          {isLogin ? "Don't have an account?" : "Already have an account?"}{" "}
          <button
            onClick={() => { setIsLogin(!isLogin); setError(""); }}
            className="text-ink underline-offset-4 decoration-2 decoration-editorial-red hover:underline"
          >
            {isLogin ? "Register" : "Sign In"}
          </button>
        </div>
      </div>
    </div>
  );
}