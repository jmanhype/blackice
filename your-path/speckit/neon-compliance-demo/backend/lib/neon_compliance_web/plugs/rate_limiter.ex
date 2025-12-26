defmodule NeonComplianceWeb.Plugs.RateLimiter do
  @moduledoc """
  Rate limiting plug using Hammer.

  Enforces API rate limits per OpenAPI specification:
  - Mutations (POST/PUT/PATCH/DELETE): 100 requests/minute per user
  - Queries (GET): 500 requests/minute per user
  """

  import Plug.Conn
  import Phoenix.Controller, only: [json: 2]

  @mutation_limit 100
  @query_limit 500
  @time_window 60_000

  def init(opts), do: opts

  def call(conn, _opts) do
    # Extract user identifier (IP address for unauthenticated, user_id for authenticated)
    identifier = get_user_identifier(conn)
    bucket_type = get_bucket_type(conn.method)
    limit = get_limit_for_bucket_type(bucket_type)
    bucket_key = "rate_limit:#{identifier}:#{bucket_type}"

    case Hammer.check_rate(bucket_key, @time_window, limit) do
      {:allow, count} ->
        conn
        |> put_resp_header("x-ratelimit-limit", Integer.to_string(limit))
        |> put_resp_header("x-ratelimit-remaining", Integer.to_string(limit - count))
        |> put_resp_header("x-ratelimit-reset", Integer.to_string(get_reset_time()))

      {:deny, _limit} ->        # Emit telemetry event for monitoring
        :telemetry.execute(
          [:neon_compliance, :rate_limit, :exceeded],
          %{count: 1},
          %{
            identifier: identifier,
            bucket_type: bucket_type,
            method: conn.method,
            path: conn.request_path,
            limit: limit
          }
        )

        conn
        |> put_status(429)
        |> put_resp_header("retry-after", "60")
        |> json(%{
          error: %{
            code: "RATE_LIMIT_EXCEEDED",
            message: "Rate limit exceeded. Maximum #{limit} requests per minute for #{bucket_type} requests.",
            details: %{
              limit: limit,
              window_seconds: 60,
              retry_after_seconds: 60
            }
          }
        })
        |> halt()

      {:error, reason} ->
        # Graceful degradation: if Hammer fails, allow the request but log the error
        require Logger

        Logger.error("Rate limiter error: #{inspect(reason)}",
          identifier: identifier,
          bucket_type: bucket_type,
          method: conn.method
        )

        # Emit telemetry for monitoring
        :telemetry.execute(
          [:neon_compliance, :rate_limit, :error],
          %{count: 1},
          %{reason: reason, bucket_type: bucket_type}
        )

        # Fail open: allow the request to proceed
        conn
    end
  end

  defp get_user_identifier(conn) do
    # Try to get user_id from assigns (set by auth plug)
    # Fall back to remote IP for unauthenticated requests
    # Note: RemoteIp plug parses X-Forwarded-For safely before this runs
    case conn.assigns[:current_user] do
      %{id: user_id} -> "user:#{user_id}"
      _ -> "ip:#{:inet.ntoa(conn.remote_ip)}"
    end
  end

  defp get_bucket_type(method) when method in ["POST", "PUT", "PATCH", "DELETE"], do: "mutation"
  defp get_bucket_type(_method), do: "query"

  defp get_limit_for_bucket_type("mutation"), do: @mutation_limit
  defp get_limit_for_bucket_type("query"), do: @query_limit

  defp get_reset_time do
    # Calculate when the current bucket window expires
    # Hammer uses fixed time windows, so we calculate the end of the current window
    now_ms = System.system_time(:millisecond)
    window_start_ms = div(now_ms, @time_window) * @time_window
    window_end_ms = window_start_ms + @time_window
    div(window_end_ms, 1000)  # Convert to Unix timestamp (seconds)
  end
end
