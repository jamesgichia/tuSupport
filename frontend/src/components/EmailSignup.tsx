"use client";

import { useState } from "react";

export default function EmailSignup() {
  const [email, setEmail] = useState("");
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(e: React.FormEvent) {
		e.preventDefault();

		const looksValid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
		if (!looksValid) {
			setError("Enter a valid email address.");
			return;
		}

		setError("");

		try {
			const response = await fetch("http://localhost:8000/api/v1/leads/", {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({ email }),
			});

			if (!response.ok) {
				const data = await response.json();
				setError(data.email?.[0] ?? "Something went wrong. Please try again.");
				return;
			}

			setSubmitted(true);
		} catch {
			setError("Could not reach the server. Please try again.");
		}
	}

  if (submitted) {
    return <p>Thanks — we&apos;ll notify you when tuSupport launches.</p>;
  }

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="you@example.com"
      />
      <button type="submit">Notify me</button>
      {error && <p>{error}</p>}
    </form>
  );
}
