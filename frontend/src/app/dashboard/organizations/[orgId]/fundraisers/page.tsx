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
        draft:     'bg-brand-accent/20 text-brand-accent',
        published: 'bg-brand-success/20 text-brand-success',
        closed:    'bg-surface-elevated text-text-muted',
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
                    <h1 className='text-2xl font-bold text-text-primary'>
                        Fundraisers
                    </h1>
                    <p className='text-sm text-text-secondary mt-1'>
                        {isAdmin ? 'Admin view — all statuses' : 'Member view — published only'}
                    </p>
                </div>
            </div>

            {/* Action error */}
            {actionError && (
                <p className='text-sm text-brand-danger bg-surface-elevated px-4 py-2 rounded-md'>
                    {actionError}
                </p>
            )}

            {/* States */}
            {loading && <p className='text-sm text-text-secondary'>Loading fundraisers...</p>}
            {error   && <p className='text-sm text-brand-danger'>{error}</p>}
            {!loading && !error && fundraisers.length === 0 && (
                <p className='text-sm text-text-secondary'>No fundraisers found.</p>
            )}

            {/* Fundraiser list */}
            {!loading && !error && fundraisers.map((f) => (
                <div
                    key={f.id}
                    className='bg-surface-card border border-surface-border rounded-lg px-5 py-4 space-y-3'
                >
                    {/* Card top row */}
                    <div className='flex justify-between items-start'>
                        <div className='space-y-1'>
                            <div className='flex items-center gap-2'>
                                <p className='text-sm font-semibold text-text-primary'>
                                    {f.title}
                                </p>
                                <StatusBadge status={f.status} />
                            </div>
                            <p className='text-xs text-text-secondary'>{f.description}</p>
                        </div>
                        <div className='text-right shrink-0 ml-4'>
                            <p className='text-sm font-bold text-brand-success'>
                                KES {parseFloat(f.goal_amount).toLocaleString()}
                            </p>
                            <p className='text-xs text-text-muted mt-1'>goal</p>
                        </div>
                    </div>

                    {/* Admin controls — hidden from members (UX only) */}
                    {isAdmin && (
                        <div className='flex gap-2 pt-1 border-t border-surface-border'>
                            {f.status === 'draft' && (
                                <button
                                    onClick={() => handleTransition(f.id, 'publish')}
                                    className='text-xs font-medium px-3 py-1.5 rounded-md bg-brand-primary text-white hover:opacity-90 transition-colors'
                                >
                                    Publish
                                </button>
                            )}
                            {f.status === 'published' && (
                                <button
                                    onClick={() => handleTransition(f.id, 'close')}
                                    className='text-xs font-medium px-3 py-1.5 rounded-md bg-surface-elevated0 text-white hover:opacity-90 transition-colors'
                                >
                                    Close
                                </button>
                            )}
                            {f.status === 'closed' && (
                                <span className='text-xs text-text-muted py-1.5'>
                                    No actions available
                                </span>
                            )}
                            <Link
                                href={`/dashboard/organizations/${orgId}/fundraisers/${f.id}/contributions`}
                                className='text-xs font-medium px-3 py-1.5 rounded-md border border-surface-border text-text-secondary hover:border-brand-primary hover:text-brand-primary transition-colors'
                            >
                                View contributions
                            </Link>
                        </div>
                    )}

                    {/* Member view — link only */}
                    {!isAdmin && f.status === 'published' && (
                        <div className='pt-1 border-t border-surface-border'>
                            <Link
                                href={`/dashboard/organizations/${orgId}/fundraisers/${f.id}/contributions`}
                                className='text-xs font-medium text-brand-primary hover:opacity-80 transition-colors'
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
