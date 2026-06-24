"use client";

import { useState } from "react";

export default function EmailSignup() {
  const [email, setEmail] = useState("");
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState("");

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();

    const looksValid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    if (!looksValid) {
      setError("Enter a valid email address.");
      return;
    }

    setError("");
    setSubmitted(true);
    // TODO: real submission goes here later — POST to a Django endpoint.
    // Until that endpoint exists and re-validates server-side, treat this
    // as a UI mockup, not a working signup.
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
