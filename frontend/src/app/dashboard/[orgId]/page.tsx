"use client";

import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";

export default function DashboardPage() {
  const { orgId } = useParams<{ orgId: string }>();
  const router = useRouter();
  const [orgName, setOrgName] = useState("");

  useEffect(() => {
    const stored = sessionStorage.getItem("organizations");
    if (!stored) {
      router.push("/login");
      return;
    }

    const orgs = JSON.parse(stored);
    const match = orgs.find((o: { id: number }) => o.id === Number(orgId));

    if (!match) {
      // orgId in URL doesn't match anything in the user's org list
      // Send back to org picker — don't expose that the org exists or not
      router.push("/pick-org");
      return;
    }

    setOrgName(match.name);
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

        <div className="border border-zinc-800 rounded-md px-6 py-10 text-center">
          <p className="text-sm text-zinc-500">
            Fundraisers for org <span className="text-emerald-400">#{orgId}</span> will appear here.
          </p>
        </div>
      </div>
    </main>
  );
}
