defmodule NeonCompliance.Repo do
  use Ecto.Repo,
    otp_app: :neon_compliance,
    adapter: Ecto.Adapters.Postgres
end
