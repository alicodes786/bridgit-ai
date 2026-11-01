import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Bridgit AI",
  description: "MA Associates bookkeeping assistant",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body style={{ margin: 0, fontFamily: "Segoe UI, sans-serif" }}>
        {children}
      </body>
    </html>
  );
}
