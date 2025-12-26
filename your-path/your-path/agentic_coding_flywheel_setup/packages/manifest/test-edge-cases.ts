/**
 * Edge case tests for manifest parser library
 */
import {
  parseManifestString,
  validateManifest,
  getModuleCategory,
  getTransitiveDependencies,
  searchModules,
  sortModulesByInstallOrder
} from './dist/index.js';

let passed = 0;
let failed = 0;

function test(name: string, fn: () => boolean) {
  try {
    if (fn()) {
      console.log(`  ✓ ${name}`);
      passed++;
    } else {
      console.log(`  ✗ ${name}`);
      failed++;
    }
  } catch (err) {
    console.log(`  ✗ ${name} - threw: ${err}`);
    failed++;
  }
}

console.log('\n=== Edge Case Tests ===\n');

// Test 1: Empty query in searchModules
console.log('1. searchModules edge cases');
const validManifest = `
version: 1
name: test
id: test
defaults:
  user: ubuntu
  workspace_root: /data/projects
  mode: vibe
modules:
  - id: base.core
    description: Core packages
    install: ["apt-get update"]
    verify: ["true"]
  - id: shell.zsh
    description: Zsh shell
    install: ["apt-get install zsh"]
    verify: ["zsh --version"]
`;

const result = parseManifestString(validManifest);
if (result.success && result.data) {
  test('empty query returns all modules', () => {
    const matches = searchModules(result.data!, '');
    return matches.length === 2;
  });

  test('no match returns empty array', () => {
    const matches = searchModules(result.data!, 'zzzznonexistent');
    return matches.length === 0;
  });
}

// Test 2: getModuleCategory with unusual IDs
console.log('\n2. getModuleCategory edge cases');
test('single segment ID returns the whole string', () => {
  return getModuleCategory('standalone') === 'standalone';
});

test('multi-dot ID returns first segment', () => {
  return getModuleCategory('a.b.c.d') === 'a';
});

// Test 3: Dependency cycle detection
console.log('\n3. Cycle detection');
const cyclicManifest = `
version: 1
name: cyclic
id: cyclic
defaults:
  user: ubuntu
  workspace_root: /data
  mode: vibe
modules:
  - id: a.one
    description: A
    install: ["true"]
    verify: ["true"]
    dependencies: ["b.two"]
  - id: b.two
    description: B
    install: ["true"]
    verify: ["true"]
    dependencies: ["a.one"]
`;

const cyclicResult = parseManifestString(cyclicManifest);
if (cyclicResult.success && cyclicResult.data) {
  const validation = validateManifest(cyclicResult.data);
  test('detects cycle between a.one and b.two', () => {
    return validation.errors.some(e => e.message.includes('cycle'));
  });
}

// Test 4: Self-referencing dependency
console.log('\n4. Self-referencing dependency');
const selfRefManifest = `
version: 1
name: selfref
id: selfref
defaults:
  user: ubuntu
  workspace_root: /data
  mode: vibe
modules:
  - id: self.loop
    description: Self-referencing
    install: ["true"]
    verify: ["true"]
    dependencies: ["self.loop"]
`;

const selfRefResult = parseManifestString(selfRefManifest);
if (selfRefResult.success && selfRefResult.data) {
  const validation = validateManifest(selfRefResult.data);
  test('detects self-referencing dependency', () => {
    return validation.errors.some(e => e.message.includes('cycle'));
  });
}

// Test 5: Missing dependency
console.log('\n5. Missing dependency detection');
const missingDepManifest = `
version: 1
name: missing
id: missing
defaults:
  user: ubuntu
  workspace_root: /data
  mode: vibe
modules:
  - id: a.one
    description: A
    install: ["true"]
    verify: ["true"]
    dependencies: ["nonexistent.module"]
`;

const missingResult = parseManifestString(missingDepManifest);
if (missingResult.success && missingResult.data) {
  const validation = validateManifest(missingResult.data);
  test('detects missing dependency', () => {
    return validation.errors.some(e => e.message.includes('Unknown dependency'));
  });
}

// Test 6: Duplicate module IDs
console.log('\n6. Duplicate module ID detection');
const duplicateManifest = `
version: 1
name: dupe
id: dupe
defaults:
  user: ubuntu
  workspace_root: /data
  mode: vibe
modules:
  - id: a.same
    description: First
    install: ["true"]
    verify: ["true"]
  - id: a.same
    description: Second
    install: ["true"]
    verify: ["true"]
`;

const dupeResult = parseManifestString(duplicateManifest);
if (dupeResult.success && dupeResult.data) {
  const validation = validateManifest(dupeResult.data);
  test('detects duplicate module IDs', () => {
    return validation.errors.some(e => e.message.includes('Duplicate'));
  });
}

// Test 7: Transitive dependencies with shared deps
console.log('\n7. Transitive dependencies (diamond pattern)');
const diamondManifest = `
version: 1
name: diamond
id: diamond
defaults:
  user: ubuntu
  workspace_root: /data
  mode: vibe
modules:
  - id: a.top
    description: Top
    install: ["true"]
    verify: ["true"]
    dependencies: ["b.left", "c.right"]
  - id: b.left
    description: Left
    install: ["true"]
    verify: ["true"]
    dependencies: ["d.bottom"]
  - id: c.right
    description: Right
    install: ["true"]
    verify: ["true"]
    dependencies: ["d.bottom"]
  - id: d.bottom
    description: Bottom
    install: ["true"]
    verify: ["true"]
`;

const diamondResult = parseManifestString(diamondManifest);
if (diamondResult.success && diamondResult.data) {
  const deps = getTransitiveDependencies(diamondResult.data, 'a.top');
  test('finds all transitive deps without duplicates', () => {
    // Should have b.left, c.right, d.bottom (3 unique deps)
    const ids = deps.map(d => d.id);
    return ids.length === 3 &&
           ids.includes('b.left') &&
           ids.includes('c.right') &&
           ids.includes('d.bottom');
  });

  // Test install order
  const sorted = sortModulesByInstallOrder(diamondResult.data);
  const sortedIds = sorted.map(m => m.id);
  test('install order has d.bottom before b.left and c.right', () => {
    const dIdx = sortedIds.indexOf('d.bottom');
    const bIdx = sortedIds.indexOf('b.left');
    const cIdx = sortedIds.indexOf('c.right');
    return dIdx < bIdx && dIdx < cIdx;
  });

  test('install order has b.left and c.right before a.top', () => {
    const aIdx = sortedIds.indexOf('a.top');
    const bIdx = sortedIds.indexOf('b.left');
    const cIdx = sortedIds.indexOf('c.right');
    return bIdx < aIdx && cIdx < aIdx;
  });
}

// Test 8: Invalid YAML
console.log('\n8. Invalid YAML handling');
const invalidYaml = `
version: 1
name: broken
  bad indentation here
`;

const invalidResult = parseManifestString(invalidYaml);
test('returns error for invalid YAML', () => {
  return !invalidResult.success && invalidResult.error !== undefined;
});

// Test 9: Schema validation errors
console.log('\n9. Schema validation');
const badSchema = `
version: -1
name: ""
id: test
defaults:
  user: ""
  workspace_root: /data
  mode: vibe
modules: []
`;

const badSchemaResult = parseManifestString(badSchema);
test('rejects negative version', () => {
  return !badSchemaResult.success;
});

console.log(`\n=== Results: ${passed} passed, ${failed} failed ===\n`);

if (failed > 0) {
  process.exit(1);
}
