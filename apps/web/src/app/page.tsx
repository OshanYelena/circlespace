import { ArrowRight, Heart, MessageCircle, Users } from "lucide-react";
import Link from "next/link";

export default function LandingPage() {
  return (
    <main className="landing">
      <header className="landing-nav">
        <div className="brand"><span className="brand-mark">C</span><span>CircleSpace</span></div>
        <div><Link className="text-link" href="/login">Sign in</Link><Link className="button button-small" href="/register">Join now</Link></div>
      </header>
      <section className="hero">
        <div className="eyebrow">A quieter, kinder social network</div>
        <h1>Keep your people<br />in your <em>orbit.</em></h1>
        <p>Share the moments that matter, start real conversations, and stay close to the people who make life interesting.</p>
        <div className="hero-actions">
          <Link className="button" href="/register">Create your space <ArrowRight size={18} /></Link>
          <Link className="button button-ghost" href="/login">I already belong</Link>
        </div>
        <div className="trust-row">
          <span><Users size={17} /> Friend-first feed</span>
          <span><MessageCircle size={17} /> Real conversation</span>
          <span><Heart size={17} /> No vanity metrics</span>
        </div>
      </section>
      <div className="orb orb-one" /><div className="orb orb-two" /><div className="grain" />
    </main>
  );
}

