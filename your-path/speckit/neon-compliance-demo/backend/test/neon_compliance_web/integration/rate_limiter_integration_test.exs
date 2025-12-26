defmodule NeonComplianceWeb.Integration.RateLimiterIntegrationTest do
  use NeonComplianceWeb.ConnCase, async: false

  setup do
    # Clear Hammer ETS tables between tests
    try do
      :ets.delete_all_objects(:hammer_ets_buckets)
    rescue
      _ -> :ok
    end

    :ok
  end

  describe "Rate Limiter Integration" do
    test "full HTTP request through router enforces rate limits (GET queries)", %{conn: conn} do
      # Create unique user for this test
      user_id = :erlang.unique_integer([:positive])
      conn = assign(conn, :current_user, %{id: user_id})

      # Make 500 GET requests to health endpoint (query limit)
      Enum.each(1..500, fn _ ->
        response_conn = get(conn, "/api/health")
        assert response_conn.status == 200  # Health endpoint exists and works
      end)

      # 501st request should be rate limited
      response_conn = get(conn, "/api/health")
      assert response_conn.status == 429

      response = json_response(response_conn, 429)
      assert response["error"]["code"] == "RATE_LIMIT_EXCEEDED"
      assert response["error"]["details"]["limit"] == 500
    end

    test "unauthenticated requests use IP-based rate limiting", %{conn: conn} do
      # Use unique IP to avoid test pollution
      unique_ip = {127, 0, 0, :rand.uniform(255)}
      conn = Map.put(conn, :remote_ip, unique_ip)

      # Make 500 GET requests (query limit)
      Enum.each(1..500, fn _ ->
        response = get(conn, "/api/health")
        assert response.status in [200, 404]
      end)

      # 501st should be rate limited
      response = get(conn, "/api/health")
      assert response.status == 429
    end

    test "rate limit headers are present on all responses", %{conn: conn} do
      user_id = :erlang.unique_integer([:positive])
      conn = assign(conn, :current_user, %{id: user_id})

      response = get(conn, "/api/health")

      assert Enum.any?(response.resp_headers, fn {k, _v} -> k == "x-ratelimit-limit" end)
      assert Enum.any?(response.resp_headers, fn {k, _v} -> k == "x-ratelimit-remaining" end)
      assert Enum.any?(response.resp_headers, fn {k, _v} -> k == "x-ratelimit-reset" end)
    end

    test "rate limit reset header shows correct expiry time", %{conn: conn} do
      user_id = :erlang.unique_integer([:positive])
      conn = assign(conn, :current_user, %{id: user_id})

      response = get(conn, "/api/health")

      reset_header =
        response.resp_headers
        |> Enum.find(fn {k, _v} -> k == "x-ratelimit-reset" end)
        |> elem(1)
        |> String.to_integer()

      now_unix = DateTime.utc_now() |> DateTime.to_unix()

      # Reset time should be between now and now + 60 seconds
      assert reset_header > now_unix
      assert reset_header <= now_unix + 60
    end

    test "different users have independent rate limits", %{conn: conn} do
      user1_id = :erlang.unique_integer([:positive])
      user2_id = :erlang.unique_integer([:positive])

      # User 1 hits their limit (500 GET requests for query bucket)
      conn1 = assign(conn, :current_user, %{id: user1_id})

      Enum.each(1..500, fn _ ->
        get(conn1, "/api/health")
      end)

      # 501st request should be rate limited
      assert get(conn1, "/api/health").status == 429

      # User 2 should still have their full allowance
      conn2 = assign(conn, :current_user, %{id: user2_id})
      response = get(conn2, "/api/health")
      assert response.status == 200  # Not 429
    end

    test "retry-after header is present on 429 responses", %{conn: conn} do
      user_id = :erlang.unique_integer([:positive])
      conn = assign(conn, :current_user, %{id: user_id})

      # Hit the limit (500 GET requests for query bucket)
      Enum.each(1..500, fn _ ->
        get(conn, "/api/health")
      end)

      # 501st request should have retry-after header
      response = get(conn, "/api/health")
      assert response.status == 429

      retry_after =
        response.resp_headers
        |> Enum.find(fn {k, _v} -> k == "retry-after" end)
        |> elem(1)

      assert retry_after == "60"
    end
  end
end
