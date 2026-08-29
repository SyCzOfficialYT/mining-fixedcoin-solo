import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "export",
  trailingSlash: true,
  assetPrefix: "/static/next-ui",
  poweredByHeader: false,
};

export default nextConfig;
