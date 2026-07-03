import { AdminSidebar } from "@/components/admin/AdminSidebar";
import { AdminTopbar } from "@/components/admin/AdminTopbar";

export default function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <>
      <AdminSidebar />
      <div className="lg:ml-64 min-h-screen flex flex-col">
        <AdminTopbar />
        <main className="flex-1">{children}</main>
      </div>
    </>
  );
}
