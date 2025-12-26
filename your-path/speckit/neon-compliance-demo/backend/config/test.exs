import Config

# Configure your database
#
# The MIX_TEST_PARTITION environment variable can be used
# to provide built-in test partitioning in CI environment.
# Run `mix help test` for more information.
config :neon_compliance, NeonCompliance.Repo,
  username: "postgres",
  password: "postgres",
  hostname: "localhost",
  database: "neon_compliance_test#{System.get_env("MIX_TEST_PARTITION")}",
  pool: Ecto.Adapters.SQL.Sandbox,
  pool_size: System.schedulers_online() * 2

# We don't run a server during test. If one is required,
# you can enable the server option below.
config :neon_compliance, NeonComplianceWeb.Endpoint,
  http: [ip: {127, 0, 0, 1}, port: 4002],
  secret_key_base: "BT0eZ+2vaD1asz/lCWjn2A1d/J8LEcnnsmlWdyUg7n+NabbSe5gq722txywtOAS+",
  server: false

# In test we don't send emails
config :neon_compliance, NeonCompliance.Mailer, adapter: Swoosh.Adapters.Test

# Disable swoosh api client as it is only required for production adapters
config :swoosh, :api_client, false

# Print only warnings and errors during test
config :logger, level: :warning

# Initialize plugs at runtime for faster test compilation
config :phoenix, :plug_init_mode, :runtime

# Use ETS backend for Hammer in tests (no Redis required)
config :hammer,
  backend:
    {Hammer.Backend.ETS,
     [
       expiry_ms: 60_000 * 60 * 2,
       cleanup_interval_ms: 60_000 * 10
     ]}
