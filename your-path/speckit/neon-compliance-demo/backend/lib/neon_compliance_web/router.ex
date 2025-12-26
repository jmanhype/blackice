defmodule NeonComplianceWeb.Router do
  use NeonComplianceWeb, :router

  # Get CORS origins from runtime config (set in config/runtime.exs)
  @cors_origins Application.compile_env(:neon_compliance, :cors_origins, [
                  "http://localhost:3000",
                  "http://localhost:4000"
                ])

  pipeline :api do
    plug :accepts, ["json"]
    plug RemoteIp
    plug CORSPlug,
      origin: @cors_origins,
      credentials: true,
      max_age: 86_400,
      headers: ["Authorization", "Content-Type", "Accept", "Origin"],
      methods: ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]

    plug NeonComplianceWeb.Plugs.RateLimiter
  end

  scope "/api", NeonComplianceWeb do
    pipe_through :api

    # Health check (no authentication required)
    get "/health", HealthController, :index
  end

  # Enable LiveDashboard and Swoosh mailbox preview in development
  if Application.compile_env(:neon_compliance, :dev_routes) do
    # If you want to use the LiveDashboard in production, you should put
    # it behind authentication and allow only admins to access it.
    # If your application does not have an admins-only section yet,
    # you can use Plug.BasicAuth to set up some basic authentication
    # as long as you are also using SSL (which you should anyway).
    import Phoenix.LiveDashboard.Router

    scope "/dev" do
      pipe_through [:fetch_session, :protect_from_forgery]

      live_dashboard "/dashboard", metrics: NeonComplianceWeb.Telemetry
      forward "/mailbox", Plug.Swoosh.MailboxPreview
    end
  end
end
