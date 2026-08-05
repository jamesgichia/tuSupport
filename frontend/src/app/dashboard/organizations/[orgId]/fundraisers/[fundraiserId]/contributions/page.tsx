'use client';

import apiClient from '@/lib/axios';
import { use, useEffect, useState } from 'react';

interface Contribution {
	id: number;
	fundraiser: number;
	contributor: number;
	contributor_name: string | null;
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

export default function ContributionsPage({ params }: PageProps) {
	const { orgId, fundraiserId } = use(params);

	const [contributions, setContributions] = useState<Contribution[]>([]);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState('');
	const [submitting, setSubmitting] = useState(false);
	const [submitError, setSubmitError] = useState('');
	const [submitSuccess, setSubmitSuccess] = useState('');
	const [role, setRole] = useState('');

	// Form fields
	const [amount, setAmount] = useState('');
	const [paymentMethod, setPaymentMethod] = useState('manual');
	const [phoneNumber, setPhoneNumber] = useState('');
	const [contributorName, setContributorName] = useState('');
	const [notes, setNotes] = useState('');

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

	useEffect(() => {
		const r = sessionStorage.getItem('current_role') || '';
		setRole(r);
	}, []);
	const handleSubmit = async () => {
		setSubmitting(true);
		setSubmitError('');
		setSubmitSuccess('');

		try {
			await apiClient.post(
				`/api/v1/organizations/${orgId}/fundraisers/${fundraiserId}/contributions/`,
				{
					amount,
					payment_method: paymentMethod,
					phone_number:
						paymentMethod === 'mpesa' ? phoneNumber : undefined,
					contributor_name: contributorName || undefined,
					notes: notes || undefined,
				},
			);

			setAmount('');
			setPaymentMethod('manual');
			setPhoneNumber('');
			setContributorName('');
			setNotes('');
			setSubmitSuccess('Contribution recorded successfully.');
			fetchContributions();
		} catch (err: any) {
			const detail =
				err.response?.data?.detail ||
				err.response?.data?.phone_number?.[0] ||
				'Failed to record contribution.';
			setSubmitError(detail);
		} finally {
			setSubmitting(false);
		}
	};

	return (
		<div className='max-w-2xl mx-auto p-6 space-y-8'>
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
					{/* Amount */}
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
							className='w-full border border-surface-border rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-primary'
						/>
					</div>

					{/* Contributor name — for unregistered cash payers */}
					{role === 'admin' && (
						<div>
							<label className='block text-sm font-medium text-text-secondary mb-1'>
								Contributor name{' '}
								<span className='text-text-muted'>
									(optional)
								</span>
							</label>
							<input
								type='text'
								value={contributorName}
								onChange={(e) =>
									setContributorName(e.target.value)
								}
								placeholder='e.g. John Kamau'
								className='w-full border border-surface-border rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-primary'
							/>
						</div>
					)}

					{/* Payment method */}
					<div>
						<label className='block text-sm font-medium text-text-secondary mb-1'>
							Payment method
						</label>
						<select
							value={paymentMethod}
							onChange={(e) => setPaymentMethod(e.target.value)}
							className='w-full border border-surface-border rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-primary'>
							<option value='manual'>Manual / Cash</option>
							<option value='mpesa'>M-Pesa</option>
						</select>
					</div>

					{/* Phone number — only shown for M-Pesa */}
					{paymentMethod === 'mpesa' && (
						<div>
							<label className='block text-sm font-medium text-text-secondary mb-1'>
								Phone number
							</label>
							<input
								type='tel'
								value={phoneNumber}
								onChange={(e) => setPhoneNumber(e.target.value)}
								placeholder='e.g. 0712345678'
								maxLength={15}
								className='w-full border border-surface-border rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-primary'
							/>
						</div>
					)}

					{/* Notes */}
					<div>
						<label className='block text-sm font-medium text-text-secondary mb-1'>
							Notes{' '}
							<span className='text-text-muted'>(optional)</span>
						</label>
						<textarea
							value={notes}
							onChange={(e) => setNotes(e.target.value)}
							placeholder='Any additional details...'
							rows={2}
							maxLength={2000}
							className='w-full border border-surface-border rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-primary'
						/>
					</div>
				</div>

				{submitError && (
					<p className='text-sm text-brand-danger'>{submitError}</p>
				)}
				{submitSuccess && (
					<p className='text-sm text-brand-success'>
						{submitSuccess}
					</p>
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
								{/* Show contributor_name if present, fall back to ID */}
								<p className='text-sm font-medium text-text-primary'>
									{c.contributor_name ||
										`Contributor #${c.contributor}`}
								</p>
								<p className='text-xs text-text-secondary'>
									{c.payment_method} ·{' '}
									{c.phone_number ||
										c.transaction_id ||
										'No reference'}{' '}
									·{' '}
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
