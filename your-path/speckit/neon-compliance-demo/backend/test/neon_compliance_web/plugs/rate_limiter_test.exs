defmodule NeonComplianceWeb.Plugs.RateLimiterTest do
  use NeonComplianceWeb.ConnCase, async: false

  alias NeonComplianceWeb.Plugs.RateLimiter

  setup do
    # Clear Hammer ETS tables between tests to prevent pollution
    # Note: In production, Redis is used, so this only affects tests
    try do
      :ets.delete_all_objects(:hammer_ets_buckets)
    rescue
      _ -> :ok
    end

    :ok
  end

  describe "Rate Limiter" do
    test "allows requests under mutation limit", %{conn: conn} do
      # Simulate 5 POST requests (well under 100/min limit)
      Enum.each(1..5, fn _ ->
        conn = conn
        |> Map.put(:method, "POST")
        |> RateLimiter.call([])

        refute conn.halted
        assert get_resp_header(conn, "x-ratelimit-limit") == ["100"]
      end)
    end

    test "allows requests under query limit", %{conn: conn} do
      # Simulate 10 GET requests (well under 500/min limit)
      Enum.each(1..10, fn _ ->
        conn = conn
        |> Map.put(:method, "GET")
        |> RateLimiter.call([])

        refute conn.halted
        assert get_resp_header(conn, "x-ratelimit-limit") == ["500"]
      end)
    end

    test "adds rate limit headers to response", %{conn: conn} do
      conn = conn
      |> Map.put(:method, "GET")
      |> RateLimiter.call([])

      assert [limit] = get_resp_header(conn, "x-ratelimit-limit")
      assert [remaining] = get_resp_header(conn, "x-ratelimit-remaining")
      assert [reset] = get_resp_header(conn, "x-ratelimit-reset")

      assert String.to_integer(limit) == 500
      assert String.to_integer(remaining) <= 500
      assert String.to_integer(reset) > 0
    end

    test "returns 429 when rate limit exceeded", %{conn: conn} do
      # Use unique user ID to avoid test pollution
      user_id = :erlang.unique_integer([:positive])
      conn = assign(conn, :current_user, %{id: user_id})

      # Make 101 POST requests to exceed 100/min mutation limit
      results =
        for i <- 1..101 do
          test_conn =
            conn
            |> Map.put(:method, "POST")
            |> Map.put(:request_path, "/api/test")
            |> RateLimiter.call([])

          {i, test_conn.status, test_conn.halted, test_conn}
        end

      # First 100 should succeed
      Enum.take(results, 100)
      |> Enum.each(fn {_i, _status, halted, _conn} ->
        refute halted, "Request should not be halted"
      end)

      # 101st should be rate limited
      {_, status, halted, limited_conn} = Enum.at(results, 100)
      assert status == 429, "Expected 429 status on 101st request"
      assert halted, "Request should be halted"

      # Verify error response structure
      assert get_resp_header(limited_conn, "retry-after") == ["60"]

      response = Jason.decode!(limited_conn.resp_body)
      assert response["error"]["code"] == "RATE_LIMIT_EXCEEDED"
      assert response["error"]["details"]["limit"] == 100
      assert response["error"]["details"]["window_seconds"] == 60
    end

    test "uses different limits for mutations vs queries", %{conn: conn} do
      # Test POST (mutation)
      post_conn = conn
      |> Map.put(:method, "POST")
      |> RateLimiter.call([])

      assert get_resp_header(post_conn, "x-ratelimit-limit") == ["100"]

      # Test GET (query)
      get_conn = conn
      |> Map.put(:method, "GET")
      |> RateLimiter.call([])

      assert get_resp_header(get_conn, "x-ratelimit-limit") == ["500"]
    end

    test "POST and PUT share same mutation bucket", %{conn: conn} do
      # Verify that all mutation methods (POST, PUT, PATCH, DELETE) share same bucket
      user_id = :erlang.unique_integer([:positive])
      conn = assign(conn, :current_user, %{id: user_id})

      # Make 60 POST requests
      Enum.each(1..60, fn _ ->
        conn
        |> Map.put(:method, "POST")
        |> RateLimiter.call([])
      end)

      # Make 40 PUT requests
      Enum.each(1..40, fn _ ->
        conn
        |> Map.put(:method, "PUT")
        |> RateLimiter.call([])
      end)

      # 101st mutation request (another PUT) should be denied
      conn_101 =
        conn
        |> Map.put(:method, "PUT")
        |> RateLimiter.call([])

      assert conn_101.status == 429
      assert conn_101.halted
    end

    test "mutations and queries have separate buckets", %{conn: conn} do
      # POST (mutation) and GET (query) should have separate rate limit buckets
      user_id = :erlang.unique_integer([:positive])
      conn = assign(conn, :current_user, %{id: user_id})

      # Make POST request
      post_conn =
        conn
        |> Map.put(:method, "POST")
        |> RateLimiter.call([])

      post_remaining =
        get_resp_header(post_conn, "x-ratelimit-remaining") |> List.first() |> String.to_integer()

      # Make GET request
      get_conn =
        conn
        |> Map.put(:method, "GET")
        |> RateLimiter.call([])

      get_remaining =
        get_resp_header(get_conn, "x-ratelimit-remaining") |> List.first() |> String.to_integer()

      # GET should have much higher remaining count (500 vs 100)
      assert get_remaining > post_remaining
      assert post_remaining == 99  # 100 - 1
      assert get_remaining == 499  # 500 - 1
    end

    test "uses IP address for unauthenticated requests", %{conn: conn} do
      # Unauthenticated request should work
      # Use unique IP to avoid test pollution
      unique_ip = {127, 0, 0, :rand.uniform(255)}

      conn =
        conn
        |> Map.put(:method, "GET")
        |> Map.put(:remote_ip, unique_ip)
        |> RateLimiter.call([])

      refute conn.halted
      assert get_resp_header(conn, "x-ratelimit-limit") == ["500"]
    end

    test "uses user_id for authenticated requests", %{conn: conn} do
      # Authenticated request should work
      user_id = :erlang.unique_integer([:positive])

      conn =
        conn
        |> assign(:current_user, %{id: user_id})
        |> Map.put(:method, "GET")
        |> RateLimiter.call([])

      refute conn.halted
      assert get_resp_header(conn, "x-ratelimit-limit") == ["500"]
    end
  end
end
