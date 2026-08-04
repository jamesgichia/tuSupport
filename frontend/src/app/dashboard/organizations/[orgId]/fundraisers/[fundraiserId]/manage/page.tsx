'use client';

import apiClient from '@/lib/axios';
import { useParams, useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';

// --- Type definitions ---
interface Beneficiary {
	id: number;
	display_name: string;
	category: string;
}

interface LinkedBeneficiary {
	id: number;
	beneficiary: number;
	beneficiary_name: string;
	notes: string;
	created_at: string;
	created_by: number | null;
}

export default function ManageFundraiserPage() {
	const { orgId, fundraiserId } = useParams<{
		orgId: string;
		fundraiserId: string;
	}>();
	const router = useRouter();

	// --- State ---
	const [linked, setLinked] = useState<LinkedBeneficiary[]>([]);
	const [allBeneficiaries, setAllBeneficiaries] = useState<Beneficiary[]>([]);
	const [selectedId, setSelectedId] = useState<string>('');
	const [notes, setNotes] = useState<string>('');
	const [loading, setLoading] = useState(true);
	const [submitting, setSubmitting] = useState(false);
	const [error, setError] = useState<string | null>(null);
	const [success, setSuccess] = useState<string | null>(null);

	// --- Auth + role gate ---
	useEffect(() => {
		const token = sessionStorage.getItem('access_token');
		const role = sessionStorage.getItem('current_role');

		if (!token) {
			router.replace('/login');
			return;
		}

		// UX gate only — backend enforces on POST with 403
		if (role !== 'admin') {
			router.replace(
				`/dashboard/organizations/${orgId}/fundraisers/${fundraiserId}`,
			);
			return;
		}

		fetchData();
	}, [orgId, fundraiserId]);

	// --- Data fetching ---
	const fetchData = async () => {
		try {
			const [linkedRes, allRes] = await Promise.all([
				apiClient.get(
					`/api/v1/organizations/${orgId}/fundraisers/${fundraiserId}/beneficiaries/`,
				),
				apiClient.get(`/api/v1/organizations/${orgId}/beneficiaries/`),
			]);

			setLinked(linkedRes.data);
			setAllBeneficiaries(allRes.data);
		} catch {
			setError('Failed to load data.');
		} finally {
			setLoading(false);
		}
	};

	// --- Derived: beneficiaries not yet linked ---
	const linkedIds = new Set(linked.map((l) => l.beneficiary));
	const available = allBeneficiaries.filter((b) => !linkedIds.has(b.id));

	// --- Attach beneficiary ---
	const handleAttach = async () => {
		if (!selectedId) return;
		setSubmitting(true);
		setError(null);
		setSuccess(null);

		try {
			await apiClient.post(
				`/api/v1/organizations/${orgId}/fundraisers/${fundraiserId}/beneficiaries/`,
				{
					beneficiary: parseInt(selectedId),
					notes: notes.trim(),
				},
			);

			setSuccess('Beneficiary linked successfully.');
			setSelectedId('');
			setNotes('');
			await fetchData(); // refresh both lists
		} catch (err: any) {
			if (err.response?.status === 400) {
				setError('This beneficiary is already linked.');
			} else if (err.response?.status === 403) {
				setError('Only admins can link beneficiaries.');
			} else {
				setError('Failed to link beneficiary.');
			}
		} finally {
			setSubmitting(false);
		}
	};

	// --- Render ---
	if (loading) return <p className='p-6 text-text-muted'>Loading...</p>;

	return (
		<main className='p-6 max-w-3xl mx-auto space-y-10'>
			{/* --- Page Header --- */}
			<section>
				<h1 className='text-2xl font-bold text-text-primary'>
					Manage Beneficiaries
				</h1>
				<p className='text-text-muted mt-1 text-sm'>
					Link welfare cases to this fundraiser. Only linked
					beneficiaries appear on the public campaign page.
				</p>
			</section>

			{/* --- Attach Form --- */}
			<section className='p-5 rounded-lg border border-surface-card bg-surface-card space-y-4'>
				<h2 className='font-semibold text-text-primary'>
					Link a Beneficiary
				</h2>

				{available.length === 0 ? (
					<p className='text-sm text-text-muted'>
						All org beneficiaries are already linked to this
						fundraiser.
					</p>
				) : (
					<>
						<div>
							<label className='block text-sm text-text-muted mb-1'>
								Select Beneficiary
							</label>
							<select
								value={selectedId}
								onChange={(e) => setSelectedId(e.target.value)}
								className='w-full border border-surface-card rounded-lg px-3 py-2
                  text-text-primary bg-white text-sm'>
								<option value=''>
									— Choose a beneficiary —
								</option>
								{available.map((b) => (
									<option key={b.id} value={b.id}>
										{b.display_name} ({b.category})
									</option>
								))}
							</select>
						</div>

						<div>
							<label className='block text-sm text-text-muted mb-1'>
								Committee Notes (optional)
							</label>
							<textarea
								value={notes}
								onChange={(e) => setNotes(e.target.value)}
								rows={3}
								placeholder='e.g. Approved by committee on 3rd Aug 2026'
								className='w-full border border-surface-card rounded-lg px-3 py-2
                  text-text-primary bg-white text-sm resize-none'
							/>
						</div>

						{error && (
							<p className='text-sm text-red-500'>{error}</p>
						)}
						{success && (
							<p className='text-sm text-green-600'>{success}</p>
						)}

						<button
							onClick={handleAttach}
							disabled={!selectedId || submitting}
							className='px-5 py-2 rounded-lg bg-brand-primary text-white
                font-semibold text-sm hover:opacity-90 transition
                disabled:opacity-50 disabled:cursor-not-allowed'>
							{submitting ? 'Linking...' : 'Link Beneficiary'}
						</button>
					</>
				)}
			</section>

			{/* --- Currently Linked --- */}
			<section>
				<h2 className='font-semibold text-text-primary mb-4'>
					Currently Linked ({linked.length})
				</h2>

				{linked.length === 0 ? (
					<p className='text-sm text-text-muted'>
						No beneficiaries linked yet.
					</p>
				) : (
					<ul className='space-y-3'>
						{linked.map((l) => (
							<li
								key={l.id}
								className='p-4 rounded-lg border border-surface-card bg-surface-card'>
								<div className='flex items-center justify-between'>
									<span className='font-medium text-text-primary'>
										{l.beneficiary_name}
									</span>
									<span className='text-xs text-text-muted'>
										{new Date(
											l.created_at,
										).toLocaleDateString('en-KE')}
									</span>
								</div>
								{l.notes && (
									<p className='text-sm text-text-muted mt-1'>
										{l.notes}
									</p>
								)}
							</li>
						))}
					</ul>
				)}
			</section>

			{/* --- Navigation --- */}
			<section>
				<button
					onClick={() =>
						router.push(
							`/dashboard/organizations/${orgId}/fundraisers/${fundraiserId}`,
						)
					}
					className='text-sm text-brand-primary hover:underline'>
					← Back to fundraiser
				</button>
			</section>
		</main>
	);
}
