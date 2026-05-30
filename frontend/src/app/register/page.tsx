"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function RegisterRedirect() {
  const router = useRouter();

  useEffect(() => {
    const token = localStorage.getItem("jimamet_token");
    const role = localStorage.getItem("jimamet_role");
    if (token) {
      if (role === "ahli_gizi") {
        router.replace("/ahli-gizi");
      } else {
        router.replace("/dashboard");
      }
    } else {
      router.replace("/login?tab=register");
    }
  }, [router]);

  return null;
}
