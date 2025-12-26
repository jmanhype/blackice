defmodule NeonComplianceWeb.HealthControllerTest do
  use NeonComplianceWeb.ConnCase

  describe "GET /api/health" do
    test "returns ok when database is healthy", %{conn: conn} do
      conn = get(conn, ~p"/api/health")
      assert json_response(conn, 200)["status"] == "ok"
      assert json_response(conn, 200)["checks"]["database"] == "healthy"
    end

    test "returns timestamp in response", %{conn: conn} do
      conn = get(conn, ~p"/api/health")
      response = json_response(conn, 200)
      assert Map.has_key?(response["checks"], "timestamp")
    end
  end
end
