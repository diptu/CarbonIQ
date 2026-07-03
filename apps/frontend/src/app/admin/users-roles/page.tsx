import type { Metadata } from "next";
import { GlassCard } from "@/components/ui";

export const metadata: Metadata = {
  title: "Users & Roles",
  description: "Manage enterprise access levels and auditor scopes.",
};

const USERS = [
  { name: "Dr. Sarah Jenkins", email: "s.jenkins@carboniq.io", role: "Auditor", roleClass: "bg-secondary-container/10 border-secondary-container/30 text-secondary-container", status: "Active", lastActivity: "2 mins ago", ip: "192.168.1.1" },
  { name: "Marcus Thorne", email: "m.thorne@carboniq.io", role: "Admin", roleClass: "bg-primary-container/10 border-primary-container/30 text-primary-container", status: "Active", lastActivity: "14 mins ago", ip: "104.22.7.42" },
  { name: "Elena Rodriguez", email: "e.rod@carboniq.io", role: "Analyst", roleClass: "bg-on-surface-variant/10 border-on-surface-variant/30 text-on-surface-variant", status: "Pending", lastActivity: "Never", ip: "Invitation sent" },
  { name: "Thomas Wu", email: "t.wu@carboniq.io", role: "Viewer", roleClass: "bg-secondary/10 border-secondary/30 text-secondary", status: "Suspended", lastActivity: "3 days ago", ip: "Sec flag revoked" },
];

const ROLES = [
  { name: "Administrator", desc: "Full system oversight, terminal configuration, and user lifecycle management.", color: "border-primary-container" },
  { name: "Auditor", desc: "Read-only evidence access with specialized sign-off privileges for carbon credits.", color: "border-secondary-container" },
  { name: "Analyst", desc: "Data ingestion and visualization tools. Limited to project-specific reporting metrics.", color: "border-outline" },
  { name: "Viewer", desc: "Dashboard visibility only. No transactional or configuration permissions enabled.", color: "border-outline-variant" },
];

const STATS = [
  { label: "Average Session", value: "42m 12s" },
  { label: "Access Geographies", value: "14 Regions" },
  { label: "Critical Warnings", value: "02", color: "text-error" },
  { label: "New Invites", value: "11", color: "text-secondary-container" },
];

export default function UsersRolesPage() {
  return (
    <div className="p-6 md:p-8 max-w-7xl mx-auto w-full">
      <div className="flex flex-col md:flex-row justify-between items-end mb-10 gap-6">
        <div>
          <h1 className="font-headline-lg text-headline-lg text-primary tracking-tight mb-2">
            Users &amp; Permissions
          </h1>
          <p className="font-body-md text-body-md text-on-surface-variant max-w-2xl">
            Manage enterprise access levels, define specific auditor scopes,
            and oversee user activity across the CarbonIQ network ledger.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button className="flex items-center gap-2 px-6 py-3 bg-transparent border border-outline-variant rounded-lg font-label-md text-label-md text-on-surface hover:bg-surface-container transition-all">
            <span className="material-symbols-outlined">download</span>
            Bulk Export
          </button>
          <button className="flex items-center gap-2 px-6 py-3 bg-primary-container text-on-primary-container rounded-lg font-label-md text-label-md font-bold neon-glow hover:brightness-110 active:scale-95 transition-all">
            <span className="material-symbols-outlined">person_add</span>
            Invite New User
          </button>
        </div>
      </div>

      <div className="grid grid-cols-12 gap-gutter">
        <GlassCard className="col-span-12 lg:col-span-9 overflow-hidden shadow-2xl">
          <div className="px-6 py-4 border-b border-outline-variant flex justify-between items-center bg-surface-container/30">
            <div className="flex items-center gap-4">
              <span className="font-label-md text-label-md font-bold uppercase tracking-widest text-primary-container">
                Live Directory
              </span>
              <div className="flex items-center gap-1.5 px-3 py-1 bg-primary-container/10 rounded-full border border-primary-container/20">
                <span className="w-1.5 h-1.5 rounded-full bg-primary-container animate-pulse" />
                <span className="text-[10px] text-primary-container font-bold">
                  142 USERS ONLINE
                </span>
              </div>
            </div>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse min-w-[640px]">
              <thead>
                <tr className="bg-surface-container-low/50">
                  <th className="px-6 py-4 font-label-md text-label-md text-on-surface-variant uppercase tracking-wider">
                    User
                  </th>
                  <th className="px-6 py-4 font-label-md text-label-md text-on-surface-variant uppercase tracking-wider">
                    Role
                  </th>
                  <th className="px-6 py-4 font-label-md text-label-md text-on-surface-variant uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-4 font-label-md text-label-md text-on-surface-variant uppercase tracking-wider">
                    Last Activity
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-outline-variant/30">
                {USERS.map((user) => (
                  <tr
                    key={user.email}
                    className="hover:bg-primary-container/5 transition-colors group"
                  >
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-lg bg-surface-container-highest border border-outline-variant flex items-center justify-center text-xs font-bold text-on-surface-variant">
                          {user.name
                            .split(" ")
                            .map((n) => n[0])
                            .join("")
                            .slice(0, 2)}
                        </div>
                        <div>
                          <div className="font-label-md text-label-md font-bold group-hover:text-primary-container transition-colors">
                            {user.name}
                          </div>
                          <div className="font-body-sm text-body-sm text-on-surface-variant">
                            {user.email}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span
                        className={`px-3 py-1 rounded-full border text-[11px] font-bold uppercase tracking-wider ${user.roleClass}`}
                      >
                        {user.role}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <div
                        className={`flex items-center gap-2 ${
                          user.status === "Active"
                            ? ""
                            : user.status === "Pending"
                              ? "opacity-50"
                              : ""
                        }`}
                      >
                        <span
                          className={`w-2 h-2 rounded-full ${
                            user.status === "Active"
                              ? "bg-primary-container shadow-[0_0_8px_#00FF9D]"
                              : user.status === "Pending"
                                ? "bg-tertiary-fixed-dim"
                                : "bg-error shadow-[0_0_8px_#ffb4ab]"
                          }`}
                        />
                        <span className="font-body-sm text-body-sm font-medium">
                          {user.status}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="font-body-sm text-body-sm">
                        {user.lastActivity}
                      </div>
                      <div className="text-[10px] text-on-surface-variant uppercase tracking-tighter">
                        {user.ip}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="px-6 py-4 border-t border-outline-variant flex justify-between items-center bg-surface-container/10">
            <div className="font-body-sm text-body-sm text-on-surface-variant">
              Showing 1 to 4 of 28 users
            </div>
          </div>
        </GlassCard>

        <div className="col-span-12 lg:col-span-3 space-y-gutter">
          <GlassCard className="p-6 relative overflow-hidden">
            <h3 className="font-headline-md text-headline-md text-primary mb-4">
              Role Access
            </h3>
            <div className="space-y-6">
              {ROLES.map((role) => (
                <div
                  key={role.name}
                  className={`relative pl-4 border-l-2 ${role.color}`}
                >
                  <div className="font-label-md text-label-md font-bold text-primary mb-1">
                    {role.name}
                  </div>
                  <p className="font-body-sm text-body-sm text-on-surface-variant">
                    {role.desc}
                  </p>
                </div>
              ))}
            </div>
            <button className="mt-8 w-full py-3 border border-primary-container/30 text-primary-container font-label-md text-label-md hover:bg-primary-container/10 transition-colors rounded-lg">
              Manage Permissions Matrix
            </button>
          </GlassCard>

          <GlassCard className="p-6">
            <h4 className="font-label-md text-label-md font-bold uppercase tracking-widest text-on-surface-variant mb-4">
              Integrity Status
            </h4>
            <div className="flex items-center gap-4 mb-4">
              <div className="p-3 bg-primary-container/10 rounded-full">
                <span className="material-symbols-outlined text-primary-container">
                  verified
                </span>
              </div>
              <div>
                <div className="text-2xl font-bold text-primary">98.2%</div>
                <div className="text-[10px] text-on-surface-variant">
                  IDENTITY VERIFIED
                </div>
              </div>
            </div>
            <div className="w-full bg-surface-container-highest h-1 rounded-full overflow-hidden">
              <div className="bg-primary-container h-full w-[98%]" />
            </div>
          </GlassCard>
        </div>

        <div className="col-span-12 grid grid-cols-1 md:grid-cols-4 gap-gutter">
          {STATS.map((stat) => (
            <GlassCard key={stat.label} className="p-6 border border-outline-variant/30 flex flex-col justify-center">
              <p className="text-on-surface-variant text-[10px] uppercase font-bold tracking-widest mb-1">
                {stat.label}
              </p>
              <div
                className={`text-3xl font-headline-md font-bold ${stat.color ?? "text-primary"}`}
              >
                {stat.value}
              </div>
            </GlassCard>
          ))}
        </div>
      </div>
    </div>
  );
}
