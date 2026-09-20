import { logout } from "@/app/actions/auth";

/** A form, not a link: logging out is a mutation, and only an action can clear a cookie. */
export default function LogoutButton({ className = "" }: { className?: string }) {
  return (
    <form action={logout}>
      <button
        type="submit"
        className={`text-sm text-neutral-slate transition-colors hover:text-primary-navy cursor-pointer ${className}`}
      >
        Log out
      </button>
    </form>
  );
}
