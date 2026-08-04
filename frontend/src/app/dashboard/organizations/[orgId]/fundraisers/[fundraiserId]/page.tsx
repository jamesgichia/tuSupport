'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import apiClient from '@/lib/axios';

interface PublicBeneficiary {
  id: number;
  display_name: string;
  category: string;
  public_description: string;
  verification_status: string;
}

interface FundraiserDetail {
  id: number;
  title: string;
  description: string;
  goal_amount: string;
  current_amount: string;
  status: string;
  beneficiaries: PublicBeneficiary[];
}

export default function FundraiserDetailPage() {
  const { orgId, fundraiserId } = useParams<{
    orgId: string;
    fundraiserId: string;
  }>();
  const router = useRouter();

  const [fundraiser, setFundraiser] = useState<FundraiserDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const token = sessionStorage.getItem('access_token');
    if (!token) {
      router.replace('/login');
      return;
    }

    apiClient
      .get(`/api/v1/organizations/${orgId}/fundraisers/${fundraiserId}/`)
      .then((res) => setFundraiser(res.data))
      .catch((err) => {
        if (err.response?.status === 404) {
          router.replace('/dashboard');
        } else {
          setError('Failed to load fundraiser.');
        }
      })
      .finally(() => setLoading(false));
  }, [orgId, fundraiserId, router]);

  if (loading) return <p className="p-6 text-text-muted">Loading...</p>;
  if (error) return <p className="p-6 text-red-500">{error}</p>;
  if (!fundraiser) return null;

  const goal = parseFloat(fundraiser.goal_amount);
  const current = parseFloat(fundraiser.current_amount ?? '0');
  const progress = goal > 0 ? Math.min((current / goal) * 100, 100) : 0;

  return (
    <main className="p-6 max-w-3xl mx-auto space-y-8">

      {/* Header */}
      <section>
        <h1 className="text-2xl font-bold text-text-primary">
          {fundraiser.title}
        </h1>
        <p className="mt-2 text-text-muted">{fundraiser.description}</p>
        <span className="inline-block mt-3 px-3 py-1 rounded-full text-sm
          bg-brand-primary text-white capitalize">
          {fundraiser.status}
        </span>
      </section>

      {/* Progress */}
      <section>
        <div className="flex justify-between text-sm text-text-muted mb-1">
          <span>KES {current.toLocaleString()}</span>
          <span>Goal: KES {goal.toLocaleString()}</span>
        </div>
        <div className="w-full bg-surface-card rounded-full h-3">
          <div
            className="bg-brand-primary h-3 rounded-full transition-all"
            style={{ width: `${progress}%` }}
          />
        </div>
        <p className="text-xs text-text-muted mt-1">{progress.toFixed(1)}% funded</p>
      </section>

      {/* Beneficiaries */}
      <section>
        <h2 className="text-lg font-semibold text-text-primary mb-4">
          Who We&apos;re Supporting
        </h2>

        {fundraiser.beneficiaries.length === 0 ? (
          <p className="text-text-muted text-sm">
            No beneficiaries linked to this fundraiser yet.
          </p>
        ) : (
          <ul className="space-y-4">
            {fundraiser.beneficiaries.map((b) => (
              <li
                key={b.id}
                className="p-4 rounded-lg border border-surface-card bg-surface-card"
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="font-medium text-text-primary">
                    {b.display_name}
                  </span>
                  <span className="text-xs px-2 py-0.5 rounded-full
                    bg-brand-primary/10 text-brand-primary capitalize">
                    {b.category}
                  </span>
                </div>
                {b.public_description && (
                  <p className="text-sm text-text-muted">{b.public_description}</p>
                )}
                <p className="text-xs text-text-muted mt-2 capitalize">
                  Status: {b.verification_status}
                </p>
              </li>
            ))}
          </ul>
        )}
      </section>

      {/* Action */}
      <section>
        <button
          onClick={() =>
            router.push(
              `/dashboard/organizations/${orgId}/fundraisers/${fundraiserId}/contributions`
            )
          }
          className="px-6 py-3 rounded-lg bg-brand-primary text-white
            font-semibold hover:opacity-90 transition"
        >
          Contribute
        </button>
      </section>

    </main>
  );
}
