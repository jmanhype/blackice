defmodule NeonComplianceWeb.HealthController do
  use NeonComplianceWeb, :controller

  @moduledoc """
  Health check endpoint for monitoring and load balancers.

  Returns service health status including dependency checks.
  """

  def index(conn, _params) do
    health_checks = %{
      database: check_database(),
      timestamp: DateTime.utc_now()
    }

    status = if health_checks.database == :healthy, do: :ok, else: :service_unavailable

    conn
    |> put_status(status)
    |> json(%{
      status: if(status == :ok, do: "ok", else: "unhealthy"),
      checks: health_checks
    })
  end

  defp check_database do
    case Ecto.Adapters.SQL.query(NeonCompliance.Repo, "SELECT 1", []) do
      {:ok, _} -> :healthy
      {:error, _} -> :unhealthy
    end
  rescue
    _ -> :unhealthy
  end
end
