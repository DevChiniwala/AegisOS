"use client";

import { Toaster } from "sonner";

export function ToastProvider() {
  return (
    <Toaster
      position="top-right"
      toastOptions={{
        classNames: {
          toast: "bg-card border-border text-card-foreground",
          title: "text-foreground",
          description: "text-muted-foreground",
        },
      }}
      richColors
      closeButton
    />
  );
}
