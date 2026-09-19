import "./globals.css";

export const metadata = {
  title: "Flaky Test Finder",
  description: "Upload two test runs and find the flaky test cases.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
