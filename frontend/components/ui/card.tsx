import React from "react";

export function Card({ children }: { children: React.ReactNode }) {
  return <div className="bg-white/10 rounded-lg p-4">{children}</div>;
}

export function CardContent({ children, className = "" }: { children: React.ReactNode; className?: string }) {
  return <div className={className}>{children}</div>;
}
