import EmailSignup from "@/components/EmailSignup";
import LandingHero from "@/components/LandingHero";
import FundraiserList from "@/components/FundraiserList";

export default function Home() {
  return (
    <>
      <LandingHero />
      <EmailSignup />
      <FundraiserList />
    </>
  );
}
