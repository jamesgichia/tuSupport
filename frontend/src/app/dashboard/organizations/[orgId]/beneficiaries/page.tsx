'use client';

import apiClient from '@/lib/axios';
import { useRouter } from 'next/navigation';
import { use, useEffect, useState } from 'react';

// ── Types ────────────────────────────────────────────────────────────────────

type VerificationStatus = 'pending' | 'verified' | 'rejected';
type Category = 'medical' | 'education' | 'funeral' | 'disaster' | 'other';
interface Beneficiary {
	id: number;
	display_name: string;
	category: Category;
	verification_status: VerificationStatus;
	full_name: string;
	national_id: string;
	phone_number: string;
	relationship_to_org: string;
	internal_notes: string;
	created_at: string;
}

interface PageProps {
	params: Promise<{ orgId: string }>;
}

// ── Sub-components ───────────────────────────────────────────────────────────

function VerificationBadge({ status }: { status: VerificationStatus }) {
	const styles: Record<VerificationStatus, string> = {
		pending: 'bg-brand-accent/20 text-brand-accent',
		verified: 'bg-brand-success/20 text-brand-success',
		rejected: 'bg-brand-danger/20 text-brand-danger',
	};
	return (
		<span
			className={`text-xs font-medium px-2 py-0.5 rounded-full ${styles[status]}`}>
			{status}
		</span>
	);
}

function CategoryLabel({ category }: { category: Category }) {
	const labels: Record<Category, string> = {
		medical: 'Medical',
		education: 'Education',
		funeral: 'Funeral/Bereavement',
		disaster: 'Disaster Relief',
		other: 'Other',
	};
	return (
		<span className='text-xs text-text-muted uppercase tracking-wide'>
			{labels[category]}
		</span>
	);
}

// ── Page ─────────────────────────────────────────────────────────────────────

export default function BeneficiariesPage({ params }: PageProps) {
	const { orgId } = use(params);
	const router = useRouter();

	const [beneficiaries, setBeneficiaries] = useState<Beneficiary[]>([]);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState('');

	const [showForm, setShowForm] = useState(false);
	const [creating, setCreating] = useState(false);
	const [createError, setCreateError] = useState('');

	const [fullName, setFullName] = useState('');
	const [displayName, setDisplayName] = useState('');
	const [category, setCategory] = useState<Category>('medical');
	const [nationalId, setNationalId] = useState('');
	const [phoneNumber, setPhoneNumber] = useState('');
	const [relationshipToOrg, setRelationshipToOrg] = useState('');
	const [internalNotes, setInternalNotes] = useState('');

	// Auth gate — UX only; backend re-validates on every request
	useEffect(() => {
		const role = sessionStorage.getItem('current_role');
		if (role !== 'admin') {
			router.replace(`/dashboard/organizations/${orgId}/fundraisers`);
		}
	}, [orgId, router]);

	const fetchBeneficiaries = async () => {
		setLoading(true);
		setError('');
		try {
			const res = await apiClient.get(
				`/api/v1/organizations/${orgId}/beneficiaries/`,
			);
			setBeneficiaries(res.data);
		} catch {
			setError('Failed to load beneficiaries. Please try again.');
		} finally {
			setLoading(false);
		}
	};

	useEffect(() => {
		fetchBeneficiaries();
	}, [orgId]);

	const handleCreate = async () => {
		setCreating(true);
		setCreateError('');
		try {
			await apiClient.post(
				`/api/v1/organizations/${orgId}/beneficiaries/`,
				{
					full_name: fullName,
					display_name: displayName,
					category,
					national_id: nationalId,
					phone_number: phoneNumber,
					relationship_to_org: relationshipToOrg,
					internal_notes: internalNotes,
				},
			);
			setFullName('');
			setDisplayName('');
			setCategory('medical');
			setNationalId('');
			setPhoneNumber('');
			setRelationshipToOrg('');
			setInternalNotes('');
			setShowForm(false);
			await fetchBeneficiaries();
		} catch (err: any) {
			const detail =
				err.response?.data?.detail || 'Failed to register beneficiary.';
			setCreateError(detail);
		} finally {
			setCreating(false);
		}
	};

	return (
		<div className='max-w-2xl mx-auto p-6 space-y-6'>
			{/* Header */}
			<div className='flex justify-between items-center'>
				<div>
					<h1 className='text-2xl font-bold text-text-primary'>
						Beneficiaries
					</h1>
					<p className='text-sm text-text-secondary mt-1'>
						Admin view — welfare cases registered to this
						organisation
					</p>
				</div>
			</div>

			{/* Create form */}
			<div className='bg-surface-card border border-surface-border rounded-lg p-5 space-y-4'>
				<div className='flex justify-between items-center'>
					<h2 className='text-sm font-semibold text-text-primary'>
						Register Beneficiary
					</h2>
					<button
						onClick={() => setShowForm(!showForm)}
						className='text-xs text-brand-primary hover:opacity-80 transition-opacity'>
						{showForm ? 'Cancel' : '+ Register'}
					</button>
				</div>

				{showForm && (
					<div className='space-y-3'>
						<input
							type='text'
							placeholder='Full name (private)'
							value={fullName}
							onChange={(e) => setFullName(e.target.value)}
							className='w-full border border-surface-border rounded-md px-3 py-2 text-sm bg-surface-bg text-text-primary focus:outline-none focus:ring-2 focus:ring-brand-primary'
						/>
						<input
							type='text'
							placeholder="Display name (e.g. 'A member's family')"
							value={displayName}
							onChange={(e) => setDisplayName(e.target.value)}
							className='w-full border border-surface-border rounded-md px-3 py-2 text-sm bg-surface-bg text-text-primary focus:outline-none focus:ring-2 focus:ring-brand-primary'
						/>
						<select
							value={category}
							onChange={(e) =>
								setCategory(e.target.value as Category)
							}
							className='w-full border border-surface-border rounded-md px-3 py-2 text-sm bg-surface-bg text-text-primary focus:outline-none focus:ring-2 focus:ring-brand-primary'>
							<option value='medical'>Medical</option>
							<option value='education'>Education</option>
							<option value='funeral'>Funeral/Bereavement</option>
							<option value='disaster'>Disaster Relief</option>
							<option value='other'>Other</option>
						</select>
						<input
							type='text'
							placeholder='National ID'
							value={nationalId}
							onChange={(e) => setNationalId(e.target.value)}
							className='w-full border border-surface-border rounded-md px-3 py-2 text-sm bg-surface-bg text-text-primary focus:outline-none focus:ring-2 focus:ring-brand-primary'
						/>
						<input
							type='tel'
							placeholder='Phone number'
							value={phoneNumber}
							onChange={(e) => setPhoneNumber(e.target.value)}
							className='w-full border border-surface-border rounded-md px-3 py-2 text-sm bg-surface-bg text-text-primary focus:outline-none focus:ring-2 focus:ring-brand-primary'
						/>
						<input
							type='text'
							placeholder="Relationship to organisation (e.g. 'Member's spouse')"
							value={relationshipToOrg}
							onChange={(e) =>
								setRelationshipToOrg(e.target.value)
							}
							className='w-full border border-surface-border rounded-md px-3 py-2 text-sm bg-surface-bg text-text-primary focus:outline-none focus:ring-2 focus:ring-brand-primary'
						/>
						<textarea
							placeholder='Internal notes (admin only)'
							value={internalNotes}
							onChange={(e) => setInternalNotes(e.target.value)}
							rows={3}
							className='w-full border border-surface-border rounded-md px-3 py-2 text-sm bg-surface-bg text-text-primary focus:outline-none focus:ring-2 focus:ring-brand-primary'
						/>

						{createError && (
							<p className='text-sm text-brand-danger'>
								{createError}
							</p>
						)}

						<button
							onClick={handleCreate}
							disabled={creating}
							className='w-full bg-brand-primary text-white py-2 px-4 rounded-md text-sm font-medium hover:opacity-90 disabled:opacity-50 transition-opacity'>
							{creating
								? 'Registering...'
								: 'Register Beneficiary'}
						</button>
					</div>
				)}
			</div>

			{/* States */}
			{loading && (
				<p className='text-sm text-text-secondary'>
					Loading beneficiaries...
				</p>
			)}
			{error && <p className='text-sm text-brand-danger'>{error}</p>}
			{!loading && !error && beneficiaries.length === 0 && (
				<p className='text-sm text-text-secondary'>
					No beneficiaries registered yet.
				</p>
			)}

			{/* Beneficiary list */}
			{!loading &&
				!error &&
				beneficiaries.map((b) => (
					<div
						key={b.id}
						className='bg-surface-card border border-surface-border rounded-lg px-5 py-4 space-y-3'>
						<div className='flex justify-between items-start'>
							<div className='space-y-1'>
								<div className='flex items-center gap-2'>
									<p className='text-sm font-semibold text-text-primary'>
										{b.full_name}
									</p>
									<VerificationBadge
										status={b.verification_status}
									/>
								</div>
								<p className='text-xs text-text-secondary'>
									Display name: {b.display_name}
								</p>
								<CategoryLabel category={b.category} />
							</div>
							<div className='text-right shrink-0 ml-4 space-y-1'>
								<p className='text-xs text-text-muted'>
									ID: {b.national_id}
								</p>
								<p className='text-xs text-text-muted'>
									{b.phone_number}
								</p>
							</div>
						</div>

						{b.relationship_to_org && (
							<p className='text-xs text-text-secondary border-t border-surface-border pt-2'>
								<span className='font-medium'>
									Relationship:
								</span>{' '}
								{b.relationship_to_org}
							</p>
						)}
						{b.internal_notes && (
							<p className='text-xs text-text-secondary'>
								<span className='font-medium'>Notes:</span>{' '}
								{b.internal_notes}
							</p>
						)}
					</div>
				))}
		</div>
	);
}
