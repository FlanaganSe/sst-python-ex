/// <reference path="./.sst/platform/config.d.ts" />

export default $config({
  app(input) {
    return {
      name: "my-python-app",
      removal: input?.stage === "production" ? "retain" : "remove",
      home: "aws",
    };
  },
  async run() {
    // Simple test function with URL
    const api = new sst.aws.Function("ApiFunction", {
      handler: "functions/src/functions/api.handler",
      runtime: "python3.11",
      url: true,
      environment: {
        STAGE: $app.stage,
      },
    });

    return {
      apiUrl: api.url,
    };
  },
});