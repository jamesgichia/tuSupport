"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

type Org = {
  id: number;
  name: string;
  role: string;
};

export default function PickOrgPage() {
  const router = useRouter();
  const [orgs, setOrgs] = useState<Org[]>([]);

  useEffect(() => {
    const stored = sessionStorage.getItem("organizations");
    if (!stored) {
      router.push("/login");
      return;
    }
    setOrgs(JSON.parse(stored));
  }, [router]);

  function handleSelect(orgId: number) {
    router.push(`/dashboard/${orgId}`);
  }

  return (
    <main className="min-h-screen flex items-center justify-center bg-zinc-950 px-4">
      <div className="w-full max-w-sm">
        <div className="mb-8">
          <span className="text-2xl font-semibold tracking-tight text-white">
            tu<span className="text-emerald-400">Support</span>
          </span>
          <p className="mt-2 text-sm text-zinc-400">
            Select an organisation to continue
          </p>
        </div>

        <div className="space-y-3">
          {orgs.length === 0 && (
            <p className="text-sm text-zinc-500">
              You are not a member of any organisation.
              Contact your administrator.
            </p>
          )}

          {orgs.map((org) => (
            <button
              key={org.id}
              onClick={() => handleSelect(org.id)}
              className="w-full flex items-center justify-between bg-zinc-900 hover:bg-zinc-800 border border-zinc-700 rounded-md px-4 py-3 transition-colors group"
            >
              <span className="text-sm font-medium text-white group-hover:text-emerald-400 transition-colors">
                {org.name}
              </span>
              <span className="text-xs text-zinc-500 uppercase tracking-wide">
                {org.role}
              </span>
            </button>
          ))}
        </div>
      </div>
    </main>
  );
}
