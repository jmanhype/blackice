"use client";

import { motion } from "@/components/motion";
import {
  GitBranch,
  GitCommit,
  GitMerge,
  History,
  Terminal,
  AlertTriangle,
  Shield,
  FileX,
  Undo2,
  Eye,
  CheckCircle,
} from "lucide-react";
import {
  Section,
  Paragraph,
  CodeBlock,
  TipBox,
  Highlight,
  Divider,
  GoalBanner,
  CommandList,
  FeatureCard,
  FeatureGrid,
  InlineCode,
} from "./lesson-components";

export function GitBasicsLesson() {
  return (
    <div className="space-y-8">
      <GoalBanner>
        Master git basics and recognize dangerous operations before they happen.
      </GoalBanner>

      {/* What Is Git */}
      <Section
        title="What Is Git?"
        icon={<GitBranch className="h-5 w-5" />}
        delay={0.1}
      >
        <Paragraph>
          <Highlight>Git</Highlight> is a version control system that tracks
          changes to your code over time. Think of it like a detailed history
          of every change you&apos;ve ever made, with the ability to go back to
          any point.
        </Paragraph>

        <div className="mt-8">
          <FeatureGrid>
            <FeatureCard
              icon={<History className="h-5 w-5" />}
              title="Full History"
              description="Every change is recorded and reversible"
              gradient="from-primary/20 to-violet-500/20"
            />
            <FeatureCard
              icon={<GitBranch className="h-5 w-5" />}
              title="Branching"
              description="Work on features without affecting main code"
              gradient="from-emerald-500/20 to-teal-500/20"
            />
            <FeatureCard
              icon={<GitMerge className="h-5 w-5" />}
              title="Collaboration"
              description="Multiple people can work on the same project"
              gradient="from-amber-500/20 to-orange-500/20"
            />
            <FeatureCard
              icon={<Shield className="h-5 w-5" />}
              title="Safety Net"
              description="Recover from mistakes (if you know how)"
              gradient="from-blue-500/20 to-indigo-500/20"
            />
          </FeatureGrid>
        </div>
      </Section>

      <Divider />

      {/* Core Concepts */}
      <Section
        title="Core Concepts"
        icon={<GitCommit className="h-5 w-5" />}
        delay={0.15}
      >
        <div className="space-y-6">
          <ConceptCard
            term="Repository"
            definition="A project folder tracked by git (contains a .git directory)"
            example="git init creates a new repository"
          />
          <ConceptCard
            term="Commit"
            definition="A snapshot of your code at a point in time"
            example="Like saving a checkpoint in a game"
          />
          <ConceptCard
            term="Staging Area"
            definition="Where you prepare changes before committing"
            example="git add puts files in staging"
          />
          <ConceptCard
            term="Branch"
            definition="An independent line of development"
            example="main, feature/login, bugfix/auth"
          />
          <ConceptCard
            term="Remote"
            definition="A copy of your repository on a server (like GitHub)"
            example="origin is the default remote name"
          />
        </div>
      </Section>

      <Divider />

      {/* Essential Commands */}
      <Section
        title="Essential Commands"
        icon={<Terminal className="h-5 w-5" />}
        delay={0.2}
      >
        <CommandList
          commands={[
            {
              command: "git status",
              description: "See what's changed (run this often!)",
            },
            {
              command: "git add <file>",
              description: "Stage a file for commit",
            },
            {
              command: "git add .",
              description: "Stage all changes",
            },
            {
              command: 'git commit -m "message"',
              description: "Create a commit with a message",
            },
            {
              command: "git push",
              description: "Upload commits to remote",
            },
            {
              command: "git pull",
              description: "Download and merge remote changes",
            },
            {
              command: "git log --oneline",
              description: "View commit history",
            },
            {
              command: "git diff",
              description: "See uncommitted changes",
            },
          ]}
        />
      </Section>

      <Divider />

      {/* .gitignore */}
      <Section
        title="Understanding .gitignore"
        icon={<FileX className="h-5 w-5" />}
        delay={0.25}
      >
        <Paragraph>
          The <InlineCode>.gitignore</InlineCode> file tells git which files to
          ignore. This is <strong>critical for security</strong> because you
          never want to commit:
        </Paragraph>

        <div className="mt-6 space-y-3">
          <IgnoreItem
            pattern=".env"
            reason="Contains API keys and secrets"
            critical
          />
          <IgnoreItem
            pattern="node_modules/"
            reason="Dependencies (huge, regeneratable)"
          />
          <IgnoreItem
            pattern=".venv/"
            reason="Python virtual environments"
          />
          <IgnoreItem
            pattern="*.log"
            reason="Log files with potentially sensitive data"
          />
          <IgnoreItem
            pattern="credentials.json"
            reason="Service account keys"
            critical
          />
          <IgnoreItem
            pattern=".claude/"
            reason="Claude Code session data"
          />
        </div>

        <div className="mt-6">
          <TipBox variant="warning">
            <strong>Never commit secrets!</strong> If you accidentally commit an
            API key, consider it compromised. Rotate it immediately.
          </TipBox>
        </div>
      </Section>

      <Divider />

      {/* Branches */}
      <Section
        title="Working with Branches"
        icon={<GitBranch className="h-5 w-5" />}
        delay={0.3}
      >
        <CommandList
          commands={[
            {
              command: "git branch",
              description: "List all local branches",
            },
            {
              command: "git branch <name>",
              description: "Create a new branch",
            },
            {
              command: "git checkout <branch>",
              description: "Switch to a branch",
            },
            {
              command: "git checkout -b <name>",
              description: "Create and switch in one command",
            },
            {
              command: "git merge <branch>",
              description: "Merge branch into current branch",
            },
            {
              command: "git branch -d <name>",
              description: "Delete a merged branch",
            },
          ]}
        />

        <div className="mt-6">
          <TipBox variant="tip">
            Always create a new branch for features or experiments. Keep{" "}
            <InlineCode>main</InlineCode> stable.
          </TipBox>
        </div>
      </Section>

      <Divider />

      {/* DANGEROUS OPERATIONS - THE CRITICAL SECTION */}
      <Section
        title="Dangerous Operations"
        icon={<AlertTriangle className="h-5 w-5" />}
        delay={0.35}
      >
        <Paragraph>
          <strong className="text-red-400">
            AI agents may propose these commands.
          </strong>{" "}
          Know what they do before approving them:
        </Paragraph>

        <div className="mt-6 space-y-4">
          <DangerousCommand
            command="git reset --hard"
            effect="Destroys all uncommitted changes permanently"
            alternative="git stash (saves changes for later)"
          />
          <DangerousCommand
            command="git clean -fd"
            effect="Deletes all untracked files permanently"
            alternative="Review with git clean -n first (dry run)"
          />
          <DangerousCommand
            command="git push --force"
            effect="Overwrites remote history, can delete teammates' work"
            alternative="git push --force-with-lease (safer)"
          />
          <DangerousCommand
            command="git checkout ."
            effect="Discards all uncommitted changes to tracked files"
            alternative="git stash or commit first"
          />
          <DangerousCommand
            command="git rebase main"
            effect="Rewrites commit history (can cause conflicts)"
            alternative="Only rebase unpushed commits"
          />
          <DangerousCommand
            command="rm -rf .git"
            effect="Destroys entire repository history forever"
            alternative="There is no alternative. Never do this."
          />
        </div>

        <div className="mt-8">
          <TipBox variant="warning">
            <strong>Before approving any git command from an agent:</strong>
            <br />
            1. Run <InlineCode>git status</InlineCode> to see current state
            <br />
            2. Run <InlineCode>git stash</InlineCode> to save uncommitted work
            <br />
            3. Only then proceed with destructive commands
          </TipBox>
        </div>
      </Section>

      <Divider />

      {/* Recovery Tools */}
      <Section
        title="Recovery Tools"
        icon={<Undo2 className="h-5 w-5" />}
        delay={0.4}
      >
        <Paragraph>
          When things go wrong, these commands can help:
        </Paragraph>

        <CommandList
          commands={[
            {
              command: "git stash",
              description: "Temporarily save uncommitted changes",
            },
            {
              command: "git stash pop",
              description: "Restore stashed changes",
            },
            {
              command: "git reflog",
              description: "View history of HEAD (find lost commits)",
            },
            {
              command: "git reset --soft HEAD~1",
              description: "Undo last commit, keep changes staged",
            },
            {
              command: "git checkout <file>",
              description: "Discard changes to a specific file",
            },
            {
              command: "git revert <commit>",
              description: "Create new commit that undoes a previous one",
            },
          ]}
        />

        <div className="mt-6">
          <CodeBlock
            code={`# Lost a commit after reset --hard? Find it!
$ git reflog
# Look for your commit hash, then:
$ git checkout <hash>
# Or create a branch at that commit:
$ git branch recovery <hash>`}
            language="bash"
          />
        </div>
      </Section>

      <Divider />

      {/* Best Practices */}
      <Section
        title="Best Practices with Agents"
        icon={<Shield className="h-5 w-5" />}
        delay={0.45}
      >
        <div className="space-y-4">
          <BestPractice
            title="Commit early and often"
            description="Small commits are easier to revert. Agents work better with clear history."
          />
          <BestPractice
            title="Always run git status before destructive commands"
            description="Know what you're about to lose before you lose it."
          />
          <BestPractice
            title="Use git stash as your safety net"
            description="Stash uncommitted work before letting agents run risky operations."
          />
          <BestPractice
            title="Review agent-proposed git commands"
            description="Agents may suggest --force or reset --hard. Always understand before approving."
          />
          <BestPractice
            title="Push your work frequently"
            description="Remote backups protect against local disasters."
          />
        </div>
      </Section>

      <Divider />

      {/* Try It Now */}
      <Section
        title="Try It Now"
        icon={<Eye className="h-5 w-5" />}
        delay={0.5}
      >
        <CodeBlock
          code={`# Check your repository status
$ git status

# View recent commits
$ git log --oneline -5

# See what's in your .gitignore
$ cat .gitignore

# Practice stashing (safe to try!)
$ echo "test" > temp.txt
$ git stash
$ git stash pop
$ rm temp.txt`}
          showLineNumbers
        />
      </Section>
    </div>
  );
}

// =============================================================================
// CONCEPT CARD
// =============================================================================
function ConceptCard({
  term,
  definition,
  example,
}: {
  term: string;
  definition: string;
  example: string;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, x: -10 }}
      animate={{ opacity: 1, x: 0 }}
      whileHover={{ x: 4, scale: 1.01 }}
      className="group rounded-2xl border border-white/[0.08] bg-white/[0.02] p-5 backdrop-blur-xl transition-all duration-300 hover:border-white/[0.15] hover:bg-white/[0.04]"
    >
      <h4 className="font-bold text-primary text-lg">{term}</h4>
      <p className="text-white/70 mt-2">{definition}</p>
      <p className="text-sm text-white/50 mt-2 italic">Example: {example}</p>
    </motion.div>
  );
}

// =============================================================================
// IGNORE ITEM
// =============================================================================
function IgnoreItem({
  pattern,
  reason,
  critical,
}: {
  pattern: string;
  reason: string;
  critical?: boolean;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, x: -10 }}
      animate={{ opacity: 1, x: 0 }}
      whileHover={{ x: 4 }}
      className={`group flex items-center gap-4 p-3 rounded-xl border transition-all duration-300 ${
        critical
          ? "border-red-500/30 bg-red-500/10 hover:border-red-500/50"
          : "border-white/[0.08] bg-white/[0.02] hover:border-white/[0.15]"
      }`}
    >
      <code className={`font-mono text-sm px-2 py-1 rounded ${critical ? "bg-red-500/20 text-red-400" : "bg-white/[0.05] text-primary"}`}>
        {pattern}
      </code>
      <span className="text-sm text-white/60">{reason}</span>
      {critical && (
        <span className="ml-auto text-xs font-medium text-red-400 uppercase">Security Risk</span>
      )}
    </motion.div>
  );
}

// =============================================================================
// DANGEROUS COMMAND
// =============================================================================
function DangerousCommand({
  command,
  effect,
  alternative,
}: {
  command: string;
  effect: string;
  alternative: string;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ x: 4, scale: 1.01 }}
      className="group rounded-2xl border border-red-500/30 bg-red-500/5 p-5 backdrop-blur-xl transition-all duration-300 hover:border-red-500/50 hover:bg-red-500/10"
    >
      <div className="flex items-center gap-3 mb-3">
        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-red-500/20">
          <AlertTriangle className="h-4 w-4 text-red-400" />
        </div>
        <code className="font-mono text-red-400 font-medium">{command}</code>
      </div>
      <p className="text-sm text-white/60 mb-2">
        <strong className="text-red-400">Effect:</strong> {effect}
      </p>
      <p className="text-sm text-emerald-400/80">
        <strong>Alternative:</strong> {alternative}
      </p>
    </motion.div>
  );
}

// =============================================================================
// BEST PRACTICE
// =============================================================================
function BestPractice({
  title,
  description,
}: {
  title: string;
  description: string;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, x: -10 }}
      animate={{ opacity: 1, x: 0 }}
      whileHover={{ x: 4, scale: 1.01 }}
      className="group flex items-start gap-4 p-5 rounded-2xl border border-emerald-500/20 bg-emerald-500/5 backdrop-blur-xl transition-all duration-300 hover:border-emerald-500/40 hover:bg-emerald-500/10"
    >
      <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-emerald-500/20 text-emerald-400 shadow-lg shadow-emerald-500/10 group-hover:shadow-emerald-500/20 transition-shadow">
        <CheckCircle className="h-5 w-5" />
      </div>
      <div>
        <p className="font-semibold text-white group-hover:text-emerald-300 transition-colors">{title}</p>
        <p className="text-sm text-white/50 mt-1">{description}</p>
      </div>
    </motion.div>
  );
}
