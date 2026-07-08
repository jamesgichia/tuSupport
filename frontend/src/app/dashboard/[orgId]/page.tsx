"use client";

import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";

type Fundraiser = {
  id: number;
  title: string;
  status: string;
};

export default function DashboardPage() {
  const { orgId } = useParams<{ orgId: string }>();
  const router = useRouter();
  const [orgName, setOrgName] = useState("");
  const [fundraisers, setFundraisers] = useState<Fundraiser[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const stored = sessionStorage.getItem("organizations");
    if (!stored) {
      router.push("/login");
      return;
    }

    const orgs = JSON.parse(stored);
    const match = orgs.find((o: { id: number }) => o.id === Number(orgId));

    if (!match) {
      router.push("/pick-org");
      return;
    }

    setOrgName(match.name);

    // Fetch fundraisers for this org — org declared via URL, token from localStorage
    const token = localStorage.getItem("access_token");
    if (!token) {
      router.push("/login");
      return;
    }

    fetch(`http://localhost:8000/api/v1/organizations/${orgId}/fundraisers/`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((res) => {
        if (!res.ok) throw new Error("Failed to load fundraisers.");
        return res.json();
      })
      .then((data) => setFundraisers(data))
      .catch(() => setError("Could not load fundraisers. Try again."))
      .finally(() => setLoading(false));

  }, [orgId, router]);

  return (
    <main className="min-h-screen bg-zinc-950 px-6 py-10">
      <div className="max-w-2xl mx-auto">
        <div className="mb-8">
          <span className="text-2xl font-semibold tracking-tight text-white">
            tu<span className="text-emerald-400">Support</span>
          </span>
        </div>

        <h1 className="text-xl font-semibold text-white mb-1">{orgName}</h1>
        <p className="text-sm text-zinc-400 mb-10">Organisation dashboard</p>

        {loading && (
          <p className="text-sm text-zinc-500">Loading fundraisers...</p>
        )}

        {error && (
          <p className="text-sm text-red-400">{error}</p>
        )}

        {!loading && !error && fundraisers.length === 0 && (
          <div className="border border-zinc-800 rounded-md px-6 py-10 text-center">
            <p className="text-sm text-zinc-500">
              No fundraisers yet. Create one to get started.
            </p>
          </div>
        )}

        {!loading && fundraisers.length > 0 && (
          <div className="space-y-3">
            {fundraisers.map((f) => (
              <div
                key={f.id}
                className="border border-zinc-800 rounded-md px-4 py-3 flex items-center justify-between"
              >
                <span className="text-sm font-medium text-white">{f.title}</span>
                <span className="text-xs text-zinc-500 uppercase tracking-wide">{f.status}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </main>
  );
}
