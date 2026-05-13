"use client";

import { useEffect, useRef, useMemo } from "react";
import ForceGraph3D from "react-force-graph-3d";
import * as THREE from "three";

interface GraphNode {
  id: string;
  label: string;
  sentiment: string;
  engagement: number;
  authority_score: number;
  author_type: string;
  platform: string;
  depth: number;
  val: number;
}

interface GraphLink {
  source: string;
  target: string;
}

interface PropagationData {
  origins?: Array<{
    post_id: string;
    author: string;
    platform: string;
    text: string;
    authority_score: number;
    author_type: string;
    is_authentic: boolean;
  }>;
  cascades?: Array<{
    origin_id: string;
    origin_author: string | null;
    origin_authority_score?: number;
    origin_is_authentic?: boolean;
    nodes: Array<{
      post_id: string;
      author: string;
      platform: string;
      text?: string;
      depth: number;
      authority_score: number;
      author_type: string;
      retweets: number;
      upvotes: number;
    }>;
  }>;
  origin?: {
    post_id: string;
    author: string;
    platform: string;
    text: string;
    authority_score: number;
    author_type: string;
    is_authentic: boolean;
  };
  cascade?: Array<{
    post_id: string;
    author: string;
    platform: string;
    text?: string;
    depth: number;
    authority_score: number;
    author_type: string;
    retweets: number;
    upvotes: number;
  }>;
  chain_length?: number;
}

function getSentimentColor(sentiment: string): string {
  if (sentiment === "positive") return "#F9F9F7";
  if (sentiment === "negative") return "#CC0000";
  return "#737373";
}

export default function KnowledgeGraph({ data }: { data: PropagationData | null }) {
  const containerRef = useRef<HTMLDivElement>(null);

  const { nodes, links } = useMemo(() => {
    if (!data) return { nodes: [], links: [] };

    const graphNodes: GraphNode[] = [];
    const graphLinks: GraphLink[] = [];

    const origins = data.origins || (data.origin ? [data.origin] : []);
    const cascades = data.cascades || (data.cascade ? [{ origin_id: data.origin?.post_id || "", origin_author: data.origin?.author || null, nodes: data.cascade }] : []);

    for (const origin of origins) {
      graphNodes.push({
        id: origin.post_id,
        label: `@${origin.author}`,
        sentiment: "origin",
        engagement: origin.authority_score,
        authority_score: origin.authority_score,
        author_type: origin.author_type,
        platform: origin.platform,
        depth: 0,
        val: 8,
      });
    }

    for (const cascade of cascades) {
      const originId = cascade.origin_id;
      if (!graphNodes.find((n) => n.id === originId) && cascade.origin_author) {
        graphNodes.push({
          id: originId,
          label: `@${cascade.origin_author}`,
          sentiment: "origin",
          engagement: cascade.origin_authority_score || 50,
          authority_score: cascade.origin_authority_score || 50,
          author_type: "public",
          platform: "",
          depth: 0,
          val: 8,
        });
      }

      const deepNodes = cascade.nodes.filter((n) => n.depth > 0);
      for (const node of deepNodes) {
        if (!graphNodes.find((n) => n.id === node.post_id)) {
          graphNodes.push({
            id: node.post_id,
            label: `@${node.author}`,
            sentiment: node.author_type === "official" ? "positive" : node.author_type === "journalist" ? "positive" : "neutral",
            engagement: (node.retweets || 0) + (node.upvotes || 0),
            authority_score: node.authority_score,
            author_type: node.author_type,
            platform: node.platform,
            depth: node.depth,
            val: Math.max(3, Math.min(10, 3 + ((node.retweets || 0) + (node.upvotes || 0)) / 100)),
          });
        }

        const parentNode = cascade.nodes.find((n) => n.depth === node.depth - 1);
        if (parentNode && node.depth > 1) {
          graphLinks.push({ source: parentNode.post_id, target: node.post_id });
        } else if (node.depth === 1) {
          graphLinks.push({ source: originId, target: node.post_id });
        }
      }
    }

    if (graphNodes.length === 0) {
      graphNodes.push({
        id: "empty",
        label: "No data",
        sentiment: "neutral",
        engagement: 0,
        authority_score: 0,
        author_type: "public",
        platform: "",
        depth: 0,
        val: 1,
      });
    }

    return { nodes: graphNodes, links: graphLinks };
  }, [data]);

  if (!data || nodes.length <= 1) {
    return (
      <div className="border border-ink p-6 text-center">
        <p className="font-mono text-xs uppercase tracking-widest text-neutral-500">
          No propagation data to visualize
        </p>
      </div>
    );
  }

  const graphData = { nodes, links };

  return (
    <div ref={containerRef} className="border border-ink bg-ink">
      <div className="border-b border-neutral-700 p-4">
        <h3 className="font-serif text-lg font-bold text-newsprint">
          Knowledge Graph
        </h3>
        <p className="font-mono text-[10px] uppercase tracking-widest text-neutral-400 mt-1">
          How information propagates through the network
        </p>
      </div>
      <div style={{ height: 420 }}>
        <ForceGraph3D
          graphData={graphData}
          backgroundColor="#111111"
          nodeColor={(node: any) => {
            if (node.sentiment === "origin") return "#CC0000";
            return getSentimentColor(node.sentiment);
          }}
          nodeVal="val"
          nodeLabel={(node: any) => `${node.label}\n${node.platform} · Authority: ${node.authority_score}`}
          linkColor={() => "rgba(249, 249, 247, 0.3)"}
          linkWidth={0.5}
          linkDirectionalArrowLength={3}
          linkDirectionalArrowRelPos={1}
          linkDirectionalParticles={1}
          linkDirectionalParticleWidth={2}
          nodeThreeObject={(node: any) => {
            const geometry = new THREE.SphereGeometry(node.val * 0.4, 16, 16);
            const color = node.sentiment === "origin" ? 0xcc0000 : node.sentiment === "positive" ? 0xf9f9f7 : node.sentiment === "negative" ? 0xcc0000 : 0x737373;
            const material = new THREE.MeshBasicMaterial({ color });
            const mesh = new THREE.Mesh(geometry, material);

            if (node.sentiment === "origin") {
              const ringGeometry = new THREE.RingGeometry(node.val * 0.5, node.val * 0.6, 32);
              const ringMaterial = new THREE.MeshBasicMaterial({ color: 0xcc0000, side: THREE.DoubleSide });
              const ring = new THREE.Mesh(ringGeometry, ringMaterial);
              mesh.add(ring);
            }

            return mesh;
          }}
          enableNodeDrag={false}
          showNavInfo={false}
        />
      </div>
      <div className="flex justify-center gap-6 p-3 border-t border-neutral-700">
        <span className="flex items-center gap-2 font-mono text-xs text-newsprint">
          <span className="w-3 h-3 bg-editorial-red rounded-full inline-block" />
          Origin
        </span>
        <span className="flex items-center gap-2 font-mono text-xs text-newsprint">
          <span className="w-3 h-3 bg-newsprint rounded-full inline-block" />
          Credible
        </span>
        <span className="flex items-center gap-2 font-mono text-xs text-neutral-400">
          <span className="w-3 h-3 bg-neutral-500 rounded-full inline-block" />
          Public
        </span>
      </div>
    </div>
  );
}