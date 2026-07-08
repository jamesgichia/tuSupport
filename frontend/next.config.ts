import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
  skipTrailingSlashRedirect: true,
  generateBuildId: async () => "tusupport-build",
};

export default nextConfig;
