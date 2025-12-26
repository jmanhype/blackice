# This file is responsible for configuring your application
# and its dependencies with the aid of the Config module.
#
# This configuration file is loaded before any dependency and
# is restricted to this project.

# General application configuration
import Config

config :neon_compliance,
  ecto_repos: [NeonCompliance.Repo],
  generators: [timestamp_type: :utc_datetime]

# Configures the endpoint
config :neon_compliance, NeonComplianceWeb.Endpoint,
  url: [host: "localhost"],
  adapter: Bandit.PhoenixAdapter,
  render_errors: [
    formats: [json: NeonComplianceWeb.ErrorJSON],
    layout: false
  ],
  pubsub_server: NeonCompliance.PubSub,
  live_view: [signing_salt: "mttv0cGK"]

# Configures the mailer
#
# By default it uses the "Local" adapter which stores the emails
# locally. You can see the emails in your browser, at "/dev/mailbox".
#
# For production it's recommended to configure a different adapter
# at the `config/runtime.exs`.
config :neon_compliance, NeonCompliance.Mailer, adapter: Swoosh.Adapters.Local

# Configure esbuild (the version is required)
config :esbuild,
  version: "0.17.11",
  neon_compliance: [
    args:
      ~w(js/app.js --bundle --target=es2017 --outdir=../priv/static/assets --external:/fonts/* --external:/images/*),
    cd: Path.expand("../assets", __DIR__),
    env: %{"NODE_PATH" => Path.expand("../deps", __DIR__)}
  ]

# Configure tailwind (the version is required)
config :tailwind,
  version: "3.4.3",
  neon_compliance: [
    args: ~w(
      --config=tailwind.config.js
      --input=css/app.css
      --output=../priv/static/assets/app.css
    ),
    cd: Path.expand("../assets", __DIR__)
  ]

# Configures Elixir's Logger
# Note: JSON formatting enabled per-environment (see dev.exs, prod.exs)
config :logger, :console,
  metadata: [:request_id, :user_id, :org_id, :remote_ip, :method, :path]

# Use Jason for JSON parsing in Phoenix
config :phoenix, :json_library, Jason

# Configure Hammer for rate limiting
# Note: Use ETS for test environment, Redis for dev/prod
# Redis URL configured in config/runtime.exs
config :hammer,
  backend:
    {Hammer.Backend.Redis,
     [
       expiry_ms: 60_000 * 60 * 2,
       redis_url: "redis://localhost:6379/1"
     ]}

# Import environment specific config. This must remain at the bottom
# of this file so it overrides the configuration defined above.
import_config "#{config_env()}.exs"
