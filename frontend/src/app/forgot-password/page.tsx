import ForgotPasswordForm from "@/components/ForgotPasswordForm";
import Logo from "@/components/Logo";

export default function ForgotPassword() {
  return (
    <div className="flex min-h-screen w-full items-center justify-center bg-neutral-mist px-4 py-16">
      <div className="w-full max-w-[440px] rounded-2xl border border-neutral-border bg-white p-8">
        <div className="mb-8 flex flex-col items-center gap-3">
          <Logo size={40} />
          <h1 className="text-2xl font-bold text-primary-navy">Reset your password</h1>
          <p className="text-center text-sm text-neutral-slate">
            Give us the address you signed up with and we&rsquo;ll send a link.
          </p>
        </div>
        <ForgotPasswordForm />
      </div>
    </div>
  );
}
