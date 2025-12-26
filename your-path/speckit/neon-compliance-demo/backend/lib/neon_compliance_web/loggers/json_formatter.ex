defmodule NeonComplianceWeb.Loggers.JSONFormatter do
  @moduledoc """
  JSON formatter for structured logging.

  Outputs logs in JSON format for log aggregation systems (e.g., ELK, Datadog).
  Performance optimized to minimize overhead on high-throughput applications.
  """

  @max_message_length 10_000
  @allowed_metadata MapSet.new([:request_id, :user_id, :org_id, :remote_ip, :method, :path])

  def format(level, message, timestamp, metadata) do
    %{
      timestamp: format_timestamp(timestamp),
      level: level,
      message: truncate_message(message),
      metadata: format_metadata(metadata)
    }
    |> Jason.encode!()
    |> then(&[&1, "\n"])
  rescue
    e in Jason.EncodeError ->
      # Only catch JSON encoding errors, let other errors propagate
      IO.puts(:stderr, "JSON encoding failed: #{inspect(e)}")
      "#{level} #{message}\n"
  end

  defp format_timestamp({date, {h, m, s, ms}}) do
    with {:ok, timestamp} <-
           NaiveDateTime.from_erl({date, {h, m, s}}, {ms * 1000, 3}),
         {:ok, datetime} <- DateTime.from_naive(timestamp, "Etc/UTC") do
      DateTime.to_iso8601(datetime)
    else
      _ -> "unknown"
    end
  end

  defp format_metadata(metadata) do
    # Single-pass optimization: filter and build in one comprehension
    for {k, v} <- metadata,
        MapSet.member?(@allowed_metadata, k),
        not is_nil(v),
        into: %{},
        do: {k, v}
  end

  defp truncate_message(message) do
    str = IO.chardata_to_string(message)

    if String.length(str) > @max_message_length do
      String.slice(str, 0, @max_message_length) <> " [truncated]"
    else
      str
    end
  end
end
