"use client";

import { useState } from "react";

import Input from "@/components/Input";
import PasswordVisibilityToggle from "@/components/PasswordVisibilityToggle";

/** Input, locked to a password field, with a show/hide toggle built in. */
export default function PasswordInput({
  label,
  name,
  placeholder,
  autoComplete,
  required,
  error,
}: {
  label: string;
  name?: string;
  placeholder: string;
  autoComplete?: string;
  required?: boolean;
  error?: string;
}) {
  const [visible, setVisible] = useState(false);

  return (
    <Input
      label={label}
      name={name}
      placeholder={placeholder}
      type={visible ? "text" : "password"}
      autoComplete={autoComplete}
      required={required}
      error={error}
      rightSlot={
        <PasswordVisibilityToggle visible={visible} onToggle={() => setVisible((v) => !v)} />
      }
    />
  );
}
