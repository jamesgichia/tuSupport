'use client';

import apiClient from '@/lib/axios';
import Link from 'next/link';
import { use, useEffect, useState } from 'react';

// --- Type definitions ---
interface Fundraiser {
    id: number;
    title: string;
    description: string;
    goal_amount: string;
    status: string;
    created_at: string;
}

interface PageProps {
    params: Promise<{
        orgId: string;
    }>;
}

// --- Main page component ---
export default function FundraisersPage({ params }: PageProps) {
    const { orgId } = use(params);

    const [fundraisers, setFundraisers] = useState<Fundraiser[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        const fetchFundraisers = async () => {
            setLoading(true);
            setError('');
            try {
                const res = await apiClient.get(
                    `/api/v1/organizations/${orgId}/fundraisers/`
                );
                setFundraisers(res.data);
            } catch {
                setError('Failed to load fundraisers. Please try again.');
            } finally {
                setLoading(false);
            }
        };

        fetchFundraisers();
    }, [orgId]);

    return (
        <div className='max-w-2xl mx-auto p-6 space-y-6'>
            {/* Page header */}
            <div>
                <h1 className='text-2xl font-bold text-gray-900'>Fundraisers</h1>
                <p className='text-sm text-gray-500 mt-1'>
                    Organization #{orgId}
                </p>
            </div>

            {/* States */}
            {loading && (
                <p className='text-sm text-gray-500'>Loading fundraisers...</p>
            )}

            {error && <p className='text-sm text-red-600'>{error}</p>}

            {!loading && !error && fundraisers.length === 0 && (
                <p className='text-sm text-gray-500'>
                    No published fundraisers found for this organisation.
                </p>
            )}

            {/* Fundraiser list */}
            {!loading && !error && fundraisers.map((f) => (
                <Link
                    key={f.id}
                    href={`/dashboard/organizations/${orgId}/fundraisers/${f.id}/contributions`}
                    className='block bg-white border border-gray-200 rounded-lg px-5 py-4 hover:border-blue-400 hover:shadow-sm transition-all'
                >
                    <div className='flex justify-between items-start'>
                        <div>
                            <p className='text-sm font-semibold text-gray-900'>
                                {f.title}
                            </p>
                            <p className='text-xs text-gray-500 mt-1'>
                                {f.description}
                            </p>
                        </div>
                        <div className='text-right shrink-0 ml-4'>
                            <p className='text-sm font-bold text-green-700'>
                                KES {parseFloat(f.goal_amount).toLocaleString()}
                            </p>
                            <p className='text-xs text-gray-400 mt-1'>goal</p>
                        </div>
                    </div>
                </Link>
            ))}
        </div>
    );
}
