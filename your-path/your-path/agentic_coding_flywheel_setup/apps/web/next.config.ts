import type { NextConfig } from "next";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const configDir = dirname(fileURLToPath(import.meta.url));
const workspaceRoot = resolve(configDir, "../..");

const nextConfig: NextConfig = {
  turbopack: {
    // Bun workspaces install deps at the workspace root; Turbopack needs this
    // to resolve `next` and other packages when multiple lockfiles exist.
    root: workspaceRoot,
  },
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "raw.githubusercontent.com",
        pathname: "/Dicklesworthstone/agentic_coding_flywheel_setup/**",
      },
    ],
  },
};

export default nextConfig;
