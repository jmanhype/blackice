"use client";

import Link from "next/link";
import {
  ArrowLeft,
  BookOpen,
  ChevronRight,
  Home,
  LayoutGrid,
  Play,
  Search,
  Send,
  Settings,
  Sparkles,
  Terminal,
  Zap,
} from "lucide-react";
import React, { useState, useCallback, useEffect, useRef } from "react";
import { CommandCard, CodeBlock } from "@/components/command-card";
import { motion, springs, staggerContainer, fadeUp } from "@/components/motion";

interface CommandCategory {
  id: string;
  name: string;
  icon: React.ReactNode;
  description: string;
  gradient: string;
  commands: Array<{
    command: string;
    description: string;
  }>;
}

const categories: CommandCategory[] = [
  {
    id: "spawn",
    name: "Spawning Agents",
    icon: <Play className="h-5 w-5" />,
    description: "Create new agent sessions with different configurations",
    gradient: "from-emerald-500/20 to-teal-500/20",
    commands: [
      {
        command: "ntm spawn myproject --cc=2 --cod=1 --gmi=1",
        description: "Spawn 2 Claude, 1 Codex, 1 Gemini agents",
      },
      {
        command: "ntm spawn myproject --cc=3",
        description: "Spawn 3 Claude agents only",
      },
      {
        command: "ntm new myproject",
        description: "Create new empty session (alias for spawn with no agents)",
      },
    ],
  },
  {
    id: "send",
    name: "Sending Prompts",
    icon: <Send className="h-5 w-5" />,
    description: "Broadcast prompts to specific agents or all agents",
    gradient: "from-primary/20 to-blue-500/20",
    commands: [
      {
        command: 'ntm send myproject "your prompt here"',
        description: "Send prompt to all agents in session",
      },
      {
        command: 'ntm send myproject --cc "Claude-specific prompt"',
        description: "Send prompt only to Claude agents",
      },
      {
        command: 'ntm send myproject --cod "Codex-specific prompt"',
        description: "Send prompt only to Codex agents",
      },
      {
        command: 'ntm send myproject --gmi "Gemini-specific prompt"',
        description: "Send prompt only to Gemini agents",
      },
    ],
  },
  {
    id: "manage",
    name: "Session Management",
    icon: <LayoutGrid className="h-5 w-5" />,
    description: "Attach, list, and manage agent sessions",
    gradient: "from-violet-500/20 to-purple-500/20",
    commands: [
      {
        command: "ntm attach myproject",
        description: "Attach to session (view all agent panes)",
      },
      {
        command: "ntm list",
        description: "List all active sessions",
      },
      {
        command: "ntm status myproject",
        description: "Show session status and agent health",
      },
      {
        command: "ntm kill myproject",
        description: "Terminate all agents in session",
      },
    ],
  },
  {
    id: "palette",
    name: "Command Palette",
    icon: <Terminal className="h-5 w-5" />,
    description: "Interactive TUI for quick command access",
    gradient: "from-sky-500/20 to-cyan-500/20",
    commands: [
      {
        command: "ntm palette",
        description: "Open command palette (fuzzy search all commands)",
      },
      {
        command: "ntm palette myproject",
        description: "Open palette for specific session",
      },
      {
        command: "ntm dashboard",
        description: "Open real-time dashboard view",
      },
    ],
  },
  {
    id: "robot",
    name: "Robot Mode (Automation)",
    icon: <Settings className="h-5 w-5" />,
    description: "Machine-readable output for scripting and automation",
    gradient: "from-amber-500/20 to-orange-500/20",
    commands: [
      {
        command: "ntm --robot-status myproject",
        description: "JSON output of session status",
      },
      {
        command: "ntm --robot-plan",
        description: "JSON output of planned actions",
      },
      {
        command: "ntm list --json",
        description: "List sessions in JSON format",
      },
    ],
  },
];

function CategoryCard({ category, isSelected }: { category: CommandCategory; isSelected?: boolean }) {
  return (
    <div className={`group relative overflow-hidden rounded-2xl border border-white/[0.08] bg-white/[0.02] backdrop-blur-xl transition-all duration-500 hover:border-white/[0.15] hover:bg-white/[0.04] ${isSelected ? "ring-2 ring-primary/50 ring-offset-2 ring-offset-black" : ""}`}>
      {/* Gradient glow on hover */}
      <div className={`absolute inset-0 bg-gradient-to-br ${category.gradient} opacity-0 group-hover:opacity-100 transition-opacity duration-500`} />

      {/* Header */}
      <div className="relative flex items-center gap-4 border-b border-white/[0.06] p-5">
        {/* Icon with glow */}
        <div className="relative shrink-0">
          <div className={`absolute inset-0 bg-gradient-to-br ${category.gradient} rounded-xl blur-xl opacity-50 group-hover:opacity-80 transition-opacity duration-500 scale-110`} />
          <motion.div
            className="relative flex h-12 w-12 items-center justify-center rounded-xl bg-white/[0.08] border border-white/[0.12] text-white transition-all duration-300 group-hover:scale-110"
            whileHover={{ rotate: 5 }}
            transition={springs.snappy}
          >
            {category.icon}
          </motion.div>
        </div>
        <div className="min-w-0">
          <h3 className="text-lg font-bold text-white">{category.name}</h3>
          <p className="text-sm text-white/50">{category.description}</p>
        </div>
      </div>

      {/* Commands */}
      <div className="relative space-y-4 p-5">
        {category.commands.map((cmd, i) => (
          <CommandCard
            key={i}
            command={cmd.command}
            description={cmd.description}
          />
        ))}
      </div>
    </div>
  );
}

export default function NtmPalettePage() {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedIndex, setSelectedIndex] = useState(-1);
  const searchInputRef = useRef<HTMLInputElement>(null);

  const filteredCategories = categories
    .map((category) => ({
      ...category,
      commands: category.commands.filter(
        (cmd) =>
          cmd.command.toLowerCase().includes(searchQuery.toLowerCase()) ||
          cmd.description.toLowerCase().includes(searchQuery.toLowerCase())
      ),
    }))
    .filter((category) => category.commands.length > 0);

  // Keyboard navigation
  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      if (e.key === "/" && document.activeElement?.tagName !== "INPUT") {
        e.preventDefault();
        searchInputRef.current?.focus();
      }
      if (e.key === "Escape") {
        setSearchQuery("");
        setSelectedIndex(-1);
        searchInputRef.current?.blur();
      }
      if ((e.key === "j" || e.key === "ArrowDown") && document.activeElement?.tagName !== "INPUT") {
        e.preventDefault();
        setSelectedIndex((prev) => (prev < filteredCategories.length - 1 ? prev + 1 : prev));
      }
      if ((e.key === "k" || e.key === "ArrowUp") && document.activeElement?.tagName !== "INPUT") {
        e.preventDefault();
        setSelectedIndex((prev) => (prev > 0 ? prev - 1 : 0));
      }
    },
    [filteredCategories.length]
  );

  useEffect(() => {
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [handleKeyDown]);

  return (
    <div className="min-h-screen bg-black relative overflow-x-hidden">
      {/* Dramatic ambient background */}
      <div className="fixed inset-0 pointer-events-none">
        {/* Large primary orb */}
        <div className="absolute w-[700px] h-[700px] bg-sky-500/10 blur-[180px] rounded-full -top-48 left-1/4 animate-float" />
        {/* Secondary orb */}
        <div className="absolute w-[500px] h-[500px] bg-primary/10 blur-[150px] rounded-full top-1/2 -right-32 animate-float" style={{ animationDelay: "2s" }} />
        {/* Tertiary orb */}
        <div className="absolute w-[400px] h-[400px] bg-violet-500/8 blur-[120px] rounded-full bottom-0 left-0 animate-float" style={{ animationDelay: "4s" }} />
        {/* Grid */}
        <div className="absolute inset-0 bg-[linear-gradient(to_right,rgba(255,255,255,0.02)_1px,transparent_1px),linear-gradient(to_bottom,rgba(255,255,255,0.02)_1px,transparent_1px)] bg-[size:80px_80px]" />
      </div>

      <div className="relative mx-auto max-w-5xl px-5 py-8 sm:px-8 md:px-12 lg:py-12">
        {/* Header navigation */}
        <motion.header
          className="mb-10 flex items-center justify-between"
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={springs.smooth}
        >
          <Link
            href="/learn"
            className="group flex items-center gap-3 text-white/50 transition-all duration-300 hover:text-white"
          >
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-white/[0.05] border border-white/[0.08] transition-all duration-300 group-hover:scale-110 group-hover:bg-white/[0.1]">
              <ArrowLeft className="h-4 w-4" />
            </div>
            <span className="text-sm font-medium">Learning Hub</span>
          </Link>
          <Link
            href="/"
            className="group flex items-center gap-3 text-white/50 transition-all duration-300 hover:text-white"
          >
            <span className="text-sm font-medium">Home</span>
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-white/[0.05] border border-white/[0.08] transition-all duration-300 group-hover:scale-110 group-hover:bg-white/[0.1]">
              <Home className="h-4 w-4" />
            </div>
          </Link>
        </motion.header>

        {/* Hero section */}
        <motion.section
          className="mb-12 text-center"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ ...springs.smooth, delay: 0.1 }}
        >
          {/* Icon with glow */}
          <motion.div
            className="mb-6 inline-flex"
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ ...springs.snappy, delay: 0.2 }}
          >
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-br from-sky-400 to-blue-500 rounded-2xl blur-xl opacity-50" />
              <div className="relative flex h-18 w-18 items-center justify-center rounded-2xl bg-gradient-to-br from-sky-400/30 to-blue-500/30 border border-white/20 shadow-2xl shadow-sky-500/20">
                <LayoutGrid className="h-9 w-9 text-white drop-shadow-lg" />
              </div>
              <motion.div
                className="absolute -right-2 -top-2"
                animate={{ rotate: [0, 15, -15, 0], scale: [1, 1.2, 1] }}
                transition={{ duration: 2, repeat: Infinity, repeatDelay: 3 }}
              >
                <Sparkles className="h-5 w-5 text-sky-400" />
              </motion.div>
            </div>
          </motion.div>

          <h1 className="mb-4 font-mono text-4xl sm:text-5xl font-bold tracking-tight">
            <span className="bg-gradient-to-br from-white via-white to-white/50 bg-clip-text text-transparent">
              NTM Commands
            </span>
          </h1>
          <p className="mx-auto max-w-2xl text-lg text-white/50 leading-relaxed">
            Named Tmux Manager (NTM) is your agent cockpit. Spawn agents, send
            prompts, and manage sessions from one powerful CLI.
          </p>
        </motion.section>

        {/* Search - stunning glassmorphic */}
        <motion.div
          className="relative mb-8"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ ...springs.smooth, delay: 0.2 }}
        >
          <div className="group relative">
            {/* Glow on focus */}
            <div className="absolute -inset-1 rounded-2xl bg-gradient-to-r from-sky-500/30 via-primary/20 to-sky-500/30 blur-lg opacity-0 group-focus-within:opacity-100 transition-opacity duration-500" />

            <div className="relative">
              <Search className="absolute left-5 top-1/2 h-5 w-5 -translate-y-1/2 text-white/30 transition-colors group-focus-within:text-sky-400" />
              <input
                ref={searchInputRef}
                type="text"
                placeholder="Search commands... (press / to focus)"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                aria-label="Search NTM commands"
                className="w-full rounded-xl border border-white/[0.08] bg-white/[0.03] py-4 pl-14 pr-5 text-white placeholder:text-white/30 backdrop-blur-xl transition-all duration-300 focus:border-sky-500/50 focus:bg-white/[0.05] focus:outline-none focus:shadow-[0_0_30px_rgba(14,165,233,0.15)]"
              />
            </div>
          </div>
        </motion.div>

        {/* Quick start - premium glassmorphic card */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ ...springs.smooth, delay: 0.3 }}
          className="mb-12"
        >
          <div className="group relative overflow-hidden rounded-2xl border border-sky-500/30 bg-gradient-to-br from-sky-500/10 via-black/40 to-blue-500/5 backdrop-blur-2xl">
            {/* Glow */}
            <div className="absolute -inset-1 bg-gradient-to-r from-sky-500/20 to-blue-500/20 blur-xl opacity-50 group-hover:opacity-80 transition-opacity duration-500" />
            {/* Top accent */}
            <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-sky-400/70 to-transparent" />

            <div className="relative p-6">
              <div className="flex items-start gap-5">
                <div className="relative shrink-0">
                  <div className="absolute inset-0 bg-gradient-to-br from-sky-400 to-blue-500 rounded-xl blur-xl opacity-40 group-hover:opacity-70 transition-opacity duration-500 scale-110" />
                  <motion.div
                    className="relative flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-sky-400/30 to-blue-500/30 border border-sky-400/40 shadow-2xl shadow-sky-500/20"
                    whileHover={{ scale: 1.1, rotate: 10 }}
                    transition={springs.snappy}
                  >
                    <Zap className="h-6 w-6 text-sky-300 drop-shadow-lg" />
                  </motion.div>
                </div>
                <div className="flex-1">
                  <h2 className="mb-2 text-xl font-bold text-white">Quick Start</h2>
                  <p className="mb-5 text-white/50">
                    Start a new project with multiple agents in seconds:
                  </p>
                  <CodeBlock
                    code={`# Create a session with 2 Claude, 1 Codex, 1 Gemini
ntm spawn myproject --cc=2 --cod=1 --gmi=1

# Attach to watch agents work
ntm attach myproject

# Send a prompt to all agents
ntm send myproject "Let's build something amazing"`}
                    language="bash"
                  />
                </div>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Command categories */}
        <motion.div
          className="space-y-6"
          initial="hidden"
          animate="visible"
          variants={staggerContainer}
        >
          {filteredCategories.length > 0 ? (
            filteredCategories.map((category, index) => (
              <motion.div
                key={category.id}
                variants={fadeUp}
                whileHover={{ y: -4 }}
                transition={springs.snappy}
              >
                <CategoryCard category={category} isSelected={selectedIndex === index} />
              </motion.div>
            ))
          ) : (
            <motion.div
              className="py-20 text-center"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={springs.smooth}
            >
              <div className="relative inline-flex mb-6">
                <div className="absolute inset-0 bg-white/10 rounded-2xl blur-xl" />
                <div className="relative flex h-16 w-16 items-center justify-center rounded-2xl bg-white/[0.05] border border-white/[0.08]">
                  <Search className="h-8 w-8 text-white/30" />
                </div>
              </div>
              <p className="text-lg text-white/40">
                No commands match your search.
              </p>
            </motion.div>
          )}
        </motion.div>

        {/* Related references - glassmorphic */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ ...springs.smooth, delay: 0.5 }}
          className="mt-12"
        >
          <div className="relative overflow-hidden rounded-2xl border border-white/[0.08] bg-white/[0.02] backdrop-blur-xl p-6">
            <div className="absolute inset-0 bg-gradient-to-br from-white/[0.03] via-transparent to-transparent" />

            <h2 className="relative mb-5 flex items-center gap-3 text-lg font-bold text-white">
              <BookOpen className="h-5 w-5 text-primary" />
              Related References
            </h2>
            <div className="relative grid gap-4 sm:grid-cols-2">
              <motion.div whileHover={{ y: -2 }} transition={springs.snappy}>
                <Link
                  href="/learn/agent-commands"
                  className="group flex items-center gap-4 rounded-xl border border-white/[0.08] bg-white/[0.02] p-4 transition-all duration-300 hover:border-white/[0.15] hover:bg-white/[0.05]"
                >
                  <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-white/[0.05] border border-white/[0.08] transition-all duration-300 group-hover:scale-110">
                    <Terminal className="h-5 w-5 text-white/60 group-hover:text-white" />
                  </div>
                  <div className="flex-1">
                    <div className="font-semibold text-white group-hover:text-primary transition-colors">Agent Commands</div>
                    <div className="text-sm text-white/50">Claude, Codex, Gemini shortcuts</div>
                  </div>
                  <ChevronRight className="h-4 w-4 text-white/30 transition-transform group-hover:translate-x-1 group-hover:text-white/60" />
                </Link>
              </motion.div>
              <motion.div whileHover={{ y: -2 }} transition={springs.snappy}>
                <Link
                  href="/workflow"
                  className="group flex items-center gap-4 rounded-xl border border-white/[0.08] bg-white/[0.02] p-4 transition-all duration-300 hover:border-white/[0.15] hover:bg-white/[0.05]"
                >
                  <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-white/[0.05] border border-white/[0.08] transition-all duration-300 group-hover:scale-110">
                    <LayoutGrid className="h-5 w-5 text-white/60 group-hover:text-white" />
                  </div>
                  <div className="flex-1">
                    <div className="font-semibold text-white group-hover:text-primary transition-colors">Flywheel Workflow</div>
                    <div className="text-sm text-white/50">Full multi-agent ecosystem</div>
                  </div>
                  <ChevronRight className="h-4 w-4 text-white/30 transition-transform group-hover:translate-x-1 group-hover:text-white/60" />
                </Link>
              </motion.div>
            </div>
          </div>
        </motion.div>

        {/* Footer */}
        <motion.footer
          className="mt-12 text-center text-sm text-white/40"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ ...springs.smooth, delay: 0.6 }}
        >
          <p>
            Back to{" "}
            <Link href="/learn" className="text-primary hover:text-primary/80 transition-colors">
              Learning Hub →
            </Link>
          </p>
        </motion.footer>
      </div>
    </div>
  );
}
