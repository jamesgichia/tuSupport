'use client';

import apiClient from '@/lib/axios';
import Link from 'next/link';
import { use, useEffect, useState } from 'react';

interface Fundraiser {
    id: number;
    title: string;
    description: string;
    goal_amount: string;
    status: 'draft' | 'published' | 'closed';
    created_at: string;
}

interface PageProps {
    params: Promise<{ orgId: string }>;
}

// Status badge — visual only, not a security control
function StatusBadge({ status }: { status: Fundraiser['status'] }) {
    const styles = {
        draft:     'bg-amber-100 text-amber-800',
        published: 'bg-green-100 text-green-800',
        closed:    'bg-gray-100 text-gray-600',
    };
    return (
        <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${styles[status]}`}>
            {status}
        </span>
    );
}

export default function FundraisersPage({ params }: PageProps) {
    const { orgId } = use(params);

    const [fundraisers, setFundraisers]   = useState<Fundraiser[]>([]);
    const [loading, setLoading]           = useState(true);
    const [error, setError]               = useState('');
    const [actionError, setActionError]   = useState('');
    const [role, setRole]                 = useState('');

    // Read role from sessionStorage — UX control only
    useEffect(() => {
        const storedRole = sessionStorage.getItem('current_role') ?? '';
        setRole(storedRole);
    }, []);

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

    useEffect(() => { fetchFundraisers(); }, [orgId]);

    // Shared handler for publish and close — backend enforces auth
    const handleTransition = async (
        fundraiserId: number,
        action: 'publish' | 'close'
    ) => {
        setActionError('');
        try {
            await apiClient.post(
                `/api/v1/organizations/${orgId}/fundraisers/${fundraiserId}/${action}/`
            );
            // Refresh list to reflect new status
            await fetchFundraisers();
        } catch {
            setActionError(`Failed to ${action} fundraiser. Please try again.`);
        }
    };

    const isAdmin = role === 'admin';

    return (
        <div className='max-w-2xl mx-auto p-6 space-y-6'>
            {/* Header */}
            <div className='flex justify-between items-center'>
                <div>
                    <h1 className='text-2xl font-bold text-gray-900'>
                        Fundraisers
                    </h1>
                    <p className='text-sm text-gray-500 mt-1'>
                        {isAdmin ? 'Admin view — all statuses' : 'Member view — published only'}
                    </p>
                </div>
            </div>

            {/* Action error */}
            {actionError && (
                <p className='text-sm text-red-600 bg-red-50 px-4 py-2 rounded-md'>
                    {actionError}
                </p>
            )}

            {/* States */}
            {loading && <p className='text-sm text-gray-500'>Loading fundraisers...</p>}
            {error   && <p className='text-sm text-red-600'>{error}</p>}
            {!loading && !error && fundraisers.length === 0 && (
                <p className='text-sm text-gray-500'>No fundraisers found.</p>
            )}

            {/* Fundraiser list */}
            {!loading && !error && fundraisers.map((f) => (
                <div
                    key={f.id}
                    className='bg-white border border-gray-200 rounded-lg px-5 py-4 space-y-3'
                >
                    {/* Card top row */}
                    <div className='flex justify-between items-start'>
                        <div className='space-y-1'>
                            <div className='flex items-center gap-2'>
                                <p className='text-sm font-semibold text-gray-900'>
                                    {f.title}
                                </p>
                                <StatusBadge status={f.status} />
                            </div>
                            <p className='text-xs text-gray-500'>{f.description}</p>
                        </div>
                        <div className='text-right shrink-0 ml-4'>
                            <p className='text-sm font-bold text-green-700'>
                                KES {parseFloat(f.goal_amount).toLocaleString()}
                            </p>
                            <p className='text-xs text-gray-400 mt-1'>goal</p>
                        </div>
                    </div>

                    {/* Admin controls — hidden from members (UX only) */}
                    {isAdmin && (
                        <div className='flex gap-2 pt-1 border-t border-gray-100'>
                            {f.status === 'draft' && (
                                <button
                                    onClick={() => handleTransition(f.id, 'publish')}
                                    className='text-xs font-medium px-3 py-1.5 rounded-md bg-teal-600 text-white hover:bg-teal-700 transition-colors'
                                >
                                    Publish
                                </button>
                            )}
                            {f.status === 'published' && (
                                <button
                                    onClick={() => handleTransition(f.id, 'close')}
                                    className='text-xs font-medium px-3 py-1.5 rounded-md bg-red-500 text-white hover:bg-red-600 transition-colors'
                                >
                                    Close
                                </button>
                            )}
                            {f.status === 'closed' && (
                                <span className='text-xs text-gray-400 py-1.5'>
                                    No actions available
                                </span>
                            )}
                            <Link
                                href={`/dashboard/organizations/${orgId}/fundraisers/${f.id}/contributions`}
                                className='text-xs font-medium px-3 py-1.5 rounded-md border border-gray-200 text-gray-600 hover:border-teal-400 hover:text-teal-700 transition-colors'
                            >
                                View contributions
                            </Link>
                        </div>
                    )}

                    {/* Member view — link only */}
                    {!isAdmin && f.status === 'published' && (
                        <div className='pt-1 border-t border-gray-100'>
                            <Link
                                href={`/dashboard/organizations/${orgId}/fundraisers/${f.id}/contributions`}
                                className='text-xs font-medium text-teal-600 hover:text-teal-800 transition-colors'
                            >
                                View contributions →
                            </Link>
                        </div>
                    )}
                </div>
            ))}
        </div>
    );
}
