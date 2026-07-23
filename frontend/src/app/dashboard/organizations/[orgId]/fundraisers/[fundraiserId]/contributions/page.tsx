'use client';

import apiClient from '@/lib/axios';
import { use, useEffect, useState } from 'react';

// --- Type definitions ---
interface Contribution {
	id: number;
	fundraiser: number;
	contributor: number;
	amount: string;
	payment_method: string;
	phone_number: string | null;
	transaction_id: string | null;
	notes: string | null;
	created_at: string;
}

interface PageProps {
	params: Promise<{
		orgId: string;
		fundraiserId: string;
	}>;
}

// --- Main page component ---
export default function ContributionsPage({ params }: PageProps) {
	// Next.js 15: params is a Promise — unwrap it with React's use()
	const { orgId, fundraiserId } = use(params);

	// --- State ---
	const [contributions, setContributions] = useState<Contribution[]>([]);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState('');
	const [submitting, setSubmitting] = useState(false);
	const [submitError, setSubmitError] = useState('');
	const [submitSuccess, setSubmitSuccess] = useState('');

	// Form fields
	const [amount, setAmount] = useState('');
	const [paymentMethod, setPaymentMethod] = useState('manual');
	const [transactionId, setTransactionId] = useState('');

	// --- Fetch contributions on mount ---
	const fetchContributions = async () => {
		setLoading(true);
		setError('');
		try {
			const res = await apiClient.get(
				`/api/v1/organizations/${orgId}/fundraisers/${fundraiserId}/contributions/`,
			);
			setContributions(res.data);
		} catch {
			setError('Failed to load contributions. Please try again.');
		} finally {
			setLoading(false);
		}
	};

	useEffect(() => {
		fetchContributions();
	}, [orgId, fundraiserId]);

	// --- Submit new contribution ---
	const handleSubmit = async () => {
		setSubmitting(true);
		setSubmitError('');
		setSubmitSuccess('');

		try {
			await apiClient.post(
				`/api/v1/organizations/${orgId}/fundraisers/${fundraiserId}/contributions/`,
				{
					amount: amount,
					payment_method: paymentMethod,
					transaction_id: transactionId || undefined,
				},
			);

			// Reset form
			setAmount('');
			setPaymentMethod('manual');
			setTransactionId('');
			setSubmitSuccess('Contribution recorded successfully.');

			// Refresh the list
			fetchContributions();
		} catch (err: any) {
			const detail =
				err.response?.data?.detail || 'Failed to record contribution.';
			setSubmitError(detail);
		} finally {
			setSubmitting(false);
		}
	};

	// --- Render ---
	return (
		<div className='max-w-2xl mx-auto p-6 space-y-8'>
			{/* Page header */}
			<div>
				<h1 className='text-2xl font-bold text-text-primary'>
					Contributions
				</h1>
				<p className='text-sm text-text-secondary mt-1'>
					Fundraiser #{fundraiserId} · Organization #{orgId}
				</p>
			</div>

			{/* Contribution form */}
			<div className='bg-surface-card border border-surface-border rounded-lg p-6 space-y-4'>
				<h2 className='text-lg font-semibold text-text-primary'>
					Record a Contribution
				</h2>

				<div className='space-y-3'>
					<div>
						<label className='block text-sm font-medium text-text-secondary mb-1'>
							Amount (KES)
						</label>
						<input
							type='number'
							value={amount}
							onChange={(e) => setAmount(e.target.value)}
							placeholder='e.g. 500'
							min='1'
							className='w-full border border-surface-border rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500'
						/>
					</div>

					<div>
						<label className='block text-sm font-medium text-text-secondary mb-1'>
							Payment Method
						</label>
						<select
							value={paymentMethod}
							onChange={(e) => setPaymentMethod(e.target.value)}
							className='w-full border border-surface-border rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500'>
							<option value='manual'>Manual / Cash</option>
							<option value='mpesa'>M-Pesa</option>
							<option value='bank'>Bank Transfer</option>
						</select>
					</div>

					<div>
						<label className='block text-sm font-medium text-text-secondary mb-1'>
							Transaction ID{' '}
							<span className='text-text-muted'>
								(optional for manual)
							</span>
						</label>
						<input
							type='text'
							value={transactionId}
							onChange={(e) => setTransactionId(e.target.value)}
							placeholder='e.g. QHJ72KXLMN'
							className='w-full border border-surface-border rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500'
						/>
					</div>
				</div>

				{/* Feedback messages */}
				{submitError && (
					<p className='text-sm text-brand-danger'>{submitError}</p>
				)}
				{submitSuccess && (
					<p className='text-sm text-brand-success'>{submitSuccess}</p>
				)}

				<button
					onClick={handleSubmit}
					disabled={submitting}
					className='w-full bg-brand-primary text-white py-2 px-4 rounded-md text-sm font-medium hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors'>
					{submitting ? 'Recording...' : 'Record Contribution'}
				</button>
			</div>

			{/* Contributions list */}
			<div className='space-y-3'>
				<h2 className='text-lg font-semibold text-text-primary'>
					Contribution History
				</h2>

				{loading && (
					<p className='text-sm text-text-secondary'>
						Loading contributions...
					</p>
				)}

				{error && <p className='text-sm text-brand-danger'>{error}</p>}

				{!loading && !error && contributions.length === 0 && (
					<p className='text-sm text-text-secondary'>
						No contributions recorded yet.
					</p>
				)}

				{!loading &&
					contributions.map((c) => (
						<div
							key={c.id}
							className='bg-surface-card border border-surface-border rounded-lg px-4 py-3 flex justify-between items-center'>
							<div>
								<p className='text-sm font-medium text-text-primary'>
									Contributor #{c.contributor}
								</p>
								<p className='text-xs text-text-secondary'>
									{c.payment_method} ·{' '}
									{c.transaction_id || 'No transaction ID'} ·{' '}
									{new Date(
										c.created_at,
									).toLocaleDateString()}
								</p>
							</div>
							<p className='text-sm font-semibold text-brand-success'>
								KES {parseFloat(c.amount).toLocaleString()}
							</p>
						</div>
					))}
			</div>
		</div>
	);
}
