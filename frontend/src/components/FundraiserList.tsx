// src/components/FundraiserList.tsx

type Fundraiser = {
  id: number;
  title: string;
  description: string;
  goal_amount: string;
  status: string;
  created_at: string;
};

async function getFundraisers(): Promise<Fundraiser[]> {
  const response = await fetch("http://localhost:8000/api/v1/fundraisers/", {
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error("Failed to fetch fundraisers");
  }

  return response.json();
}

export default async function FundraiserList() {
  const fundraisers = await getFundraisers();

  if (fundraisers.length === 0) {
    return <p>No fundraisers available yet.</p>;
  }

  return (
    <ul>
      {fundraisers.map((f) => (
        <li key={f.id}>
          <h2>{f.title}</h2>
          <p>{f.description}</p>
          <p>Goal: KES {f.goal_amount}</p>
        </li>
      ))}
    </ul>
  );
}
