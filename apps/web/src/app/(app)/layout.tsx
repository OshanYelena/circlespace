import { AppNav } from "@/components/app-nav";
import { Protected } from "@/components/protected";

export default function AuthenticatedLayout({ children }: { children: React.ReactNode }) {
  return (
    <Protected>
      <AppNav />
      <main className="app-shell">{children}</main>
    </Protected>
  );
}

