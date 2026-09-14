/** Railway service config for Slice Lens. Tests run in the Docker build. */
export default {
  build: {
    builder: "DOCKERFILE",
    dockerfilePath: "Dockerfile",
  },
  deploy: {
    healthcheckPath: "/health",
    restartPolicyType: "ON_FAILURE",
    startCommand:
      "python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}",
  },
};
