"use client";

export default function ClientShell({ children }) {
  return (
    <>
      <a href="#results-section" className="skip-nav">Skip to results</a>
      {children}
    </>
  );
}
