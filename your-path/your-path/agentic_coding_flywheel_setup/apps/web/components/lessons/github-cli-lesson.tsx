"use client";

import { motion } from "@/components/motion";
import {
  Github,
  KeyRound,
  CircleDot,
  GitPullRequest,
  Tag,
  Workflow,
  Eye,
  CheckCircle,
  Zap,
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

export function GithubCliLesson() {
  return (
    <div className="space-y-8">
      <GoalBanner>
        Manage GitHub issues, PRs, releases, and actions from the command line.
      </GoalBanner>

      {/* What Is GitHub CLI */}
      <Section
        title="What Is GitHub CLI?"
        icon={<Github className="h-5 w-5" />}
        delay={0.1}
      >
        <Paragraph>
          <Highlight>GitHub CLI (gh)</Highlight> lets you interact with GitHub
          directly from your terminal. No more switching between your editor and
          browser for common tasks.
        </Paragraph>

        <div className="mt-8">
          <FeatureGrid>
            <FeatureCard
              icon={<CircleDot className="h-5 w-5" />}
              title="Issues"
              description="Create, view, and close issues"
              gradient="from-emerald-500/20 to-teal-500/20"
            />
            <FeatureCard
              icon={<GitPullRequest className="h-5 w-5" />}
              title="Pull Requests"
              description="Create, review, and merge PRs"
              gradient="from-primary/20 to-violet-500/20"
            />
            <FeatureCard
              icon={<Tag className="h-5 w-5" />}
              title="Releases"
              description="Create tags and releases"
              gradient="from-amber-500/20 to-orange-500/20"
            />
            <FeatureCard
              icon={<Workflow className="h-5 w-5" />}
              title="Actions"
              description="View and manage workflows"
              gradient="from-blue-500/20 to-indigo-500/20"
            />
          </FeatureGrid>
        </div>

        <div className="mt-6">
          <TipBox variant="info">
            AI agents use <InlineCode>gh</InlineCode> extensively for
            GitHub operations. Understanding these commands helps you review
            what agents propose.
          </TipBox>
        </div>
      </Section>

      <Divider />

      {/* Authentication */}
      <Section
        title="Authentication"
        icon={<KeyRound className="h-5 w-5" />}
        delay={0.15}
      >
        <Paragraph>
          First, authenticate with your GitHub account:
        </Paragraph>

        <div className="mt-6">
          <CodeBlock
            code={`# Interactive login (recommended)
$ gh auth login

# Check your auth status
$ gh auth status

# View current user
$ gh api user --jq '.login'`}
            language="bash"
          />
        </div>

        <div className="mt-6">
          <TipBox variant="tip">
            The interactive login will guide you through browser-based OAuth.
            Choose HTTPS for the git protocol unless you have SSH keys set up.
          </TipBox>
        </div>
      </Section>

      <Divider />

      {/* Issues */}
      <Section
        title="Working with Issues"
        icon={<CircleDot className="h-5 w-5" />}
        delay={0.2}
      >
        <CommandList
          commands={[
            {
              command: "gh issue list",
              description: "List open issues",
            },
            {
              command: "gh issue list --state all",
              description: "List all issues (open and closed)",
            },
            {
              command: "gh issue view 123",
              description: "View issue #123 details",
            },
            {
              command: 'gh issue create --title "Bug" --body "Description"',
              description: "Create a new issue",
            },
            {
              command: "gh issue close 123",
              description: "Close issue #123",
            },
            {
              command: 'gh issue comment 123 --body "Comment text"',
              description: "Add a comment to issue #123",
            },
          ]}
        />

        <div className="mt-6">
          <CodeBlock
            code={`# Create an issue interactively
$ gh issue create

# Create with labels and assignee
$ gh issue create \\
  --title "Fix login bug" \\
  --body "Users can't login with email" \\
  --label bug \\
  --assignee @me`}
            language="bash"
          />
        </div>
      </Section>

      <Divider />

      {/* Pull Requests */}
      <Section
        title="Pull Requests"
        icon={<GitPullRequest className="h-5 w-5" />}
        delay={0.25}
      >
        <Paragraph>
          Create and manage pull requests without leaving your terminal:
        </Paragraph>

        <div className="mt-6">
          <CommandList
            commands={[
              {
                command: "gh pr list",
                description: "List open pull requests",
              },
              {
                command: "gh pr view 456",
                description: "View PR #456 details",
              },
              {
                command: "gh pr create",
                description: "Create a PR (interactive)",
              },
              {
                command: "gh pr checkout 456",
                description: "Check out PR #456 locally",
              },
              {
                command: "gh pr merge 456",
                description: "Merge PR #456",
              },
              {
                command: "gh pr diff 456",
                description: "View PR diff",
              },
            ]}
          />
        </div>

        <div className="mt-6">
          <CodeBlock
            code={`# Create a PR with title and body
$ gh pr create \\
  --title "Add user authentication" \\
  --body "## Summary
Implements OAuth2 login flow.

## Test plan
- [x] Unit tests pass
- [ ] Manual testing on staging"

# Create a draft PR
$ gh pr create --draft

# Request review
$ gh pr edit 456 --add-reviewer username

# View PR checks status
$ gh pr checks 456`}
            language="bash"
          />
        </div>

        <div className="mt-6">
          <TipBox variant="tip">
            Agents often create PRs using heredocs for the body. This format
            is common: <InlineCode>--body &quot;$(cat &lt;&lt;&apos;EOF&apos; ... EOF)&quot;</InlineCode>
          </TipBox>
        </div>
      </Section>

      <Divider />

      {/* Releases and Tags */}
      <Section
        title="Releases & Tags"
        icon={<Tag className="h-5 w-5" />}
        delay={0.3}
      >
        <CommandList
          commands={[
            {
              command: "gh release list",
              description: "List releases",
            },
            {
              command: "gh release view v1.2.0",
              description: "View release details",
            },
            {
              command: 'gh release create v1.2.0 --notes "Release notes"',
              description: "Create a release with tag",
            },
            {
              command: "gh release create v1.2.0 --generate-notes",
              description: "Auto-generate notes from commits",
            },
            {
              command: "gh release download v1.2.0",
              description: "Download release assets",
            },
          ]}
        />

        <div className="mt-6">
          <CodeBlock
            code={`# Create a release with assets
$ gh release create v2.0.0 \\
  --title "Version 2.0.0" \\
  --notes "Major update with new features" \\
  ./dist/*.zip

# Create a pre-release
$ gh release create v2.1.0-beta --prerelease

# Delete a release (be careful!)
$ gh release delete v1.0.0-test --yes`}
            language="bash"
          />
        </div>
      </Section>

      <Divider />

      {/* GitHub Actions */}
      <Section
        title="GitHub Actions"
        icon={<Workflow className="h-5 w-5" />}
        delay={0.35}
      >
        <Paragraph>
          Monitor and interact with your CI/CD workflows:
        </Paragraph>

        <div className="mt-6">
          <CommandList
            commands={[
              {
                command: "gh workflow list",
                description: "List all workflows",
              },
              {
                command: "gh run list",
                description: "List recent workflow runs",
              },
              {
                command: "gh run view 123456",
                description: "View run details",
              },
              {
                command: "gh run view 123456 --log",
                description: "View run logs",
              },
              {
                command: "gh run watch 123456",
                description: "Watch a run in real-time",
              },
              {
                command: "gh run rerun 123456",
                description: "Re-run a failed workflow",
              },
            ]}
          />
        </div>

        <div className="mt-6">
          <CodeBlock
            code={`# View failed runs
$ gh run list --status failure

# Trigger a workflow manually
$ gh workflow run build.yml

# Trigger with inputs
$ gh workflow run deploy.yml -f environment=staging

# View job logs for a specific job
$ gh run view 123456 --job 789 --log`}
            language="bash"
          />
        </div>
      </Section>

      <Divider />

      {/* Repository Info */}
      <Section
        title="Repository Operations"
        icon={<Github className="h-5 w-5" />}
        delay={0.4}
      >
        <CommandList
          commands={[
            {
              command: "gh repo view",
              description: "View current repo info",
            },
            {
              command: "gh repo clone owner/repo",
              description: "Clone a repository",
            },
            {
              command: "gh repo fork",
              description: "Fork current repo",
            },
            {
              command: "gh repo create my-project --public",
              description: "Create a new repository",
            },
            {
              command: "gh browse",
              description: "Open repo in browser",
            },
            {
              command: "gh browse issues",
              description: "Open issues page in browser",
            },
          ]}
        />
      </Section>

      <Divider />

      {/* API Access */}
      <Section
        title="Direct API Access"
        icon={<Zap className="h-5 w-5" />}
        delay={0.45}
      >
        <Paragraph>
          For advanced use cases, access the GitHub API directly:
        </Paragraph>

        <div className="mt-6">
          <CodeBlock
            code={`# Get repo info as JSON
$ gh api repos/owner/repo

# List PR comments
$ gh api repos/owner/repo/pulls/123/comments

# Use jq to extract specific fields
$ gh api user --jq '.login, .email'

# POST to create something
$ gh api repos/owner/repo/issues \\
  -f title="API created issue" \\
  -f body="Created via gh api"`}
            language="bash"
          />
        </div>

        <div className="mt-6">
          <TipBox variant="info">
            Agents use <InlineCode>gh api</InlineCode> for operations not
            covered by the standard commands. Review these carefully as they
            have full API access.
          </TipBox>
        </div>
      </Section>

      <Divider />

      {/* Best Practices */}
      <Section
        title="Best Practices"
        icon={<CheckCircle className="h-5 w-5" />}
        delay={0.5}
      >
        <div className="space-y-4">
          <BestPractice
            title="Always review PR details before merging"
            description="Use gh pr view and gh pr diff to understand changes."
          />
          <BestPractice
            title="Use --dry-run where available"
            description="Some commands support --dry-run to preview actions."
          />
          <BestPractice
            title="Check workflow status before deploying"
            description="Run gh run list to ensure CI passed before releasing."
          />
          <BestPractice
            title="Use labels and milestones"
            description="Organize issues with --label and --milestone flags."
          />
          <BestPractice
            title="Review agent-created PRs carefully"
            description="Agents may create PRs automatically. Always review before merging."
          />
        </div>
      </Section>

      <Divider />

      {/* Try It Now */}
      <Section
        title="Try It Now"
        icon={<Eye className="h-5 w-5" />}
        delay={0.55}
      >
        <CodeBlock
          code={`# Check if gh is installed and authenticated
$ gh auth status

# View the current repository
$ gh repo view

# List recent issues
$ gh issue list --limit 5

# List recent PRs
$ gh pr list --limit 5

# Check recent workflow runs
$ gh run list --limit 5`}
          showLineNumbers
        />
      </Section>
    </div>
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
