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
    const api = new sst.aws.Function("ApiFunction", {
      handler: "functions/src/functions/api.handler",
      runtime: "python3.12",
      url: true,
      environment: {
        STAGE: $app.stage,
      },
      permissions: [
        {
          actions: [
            "bedrock:Converse",
            "bedrock:ConverseStream",
            "bedrock:InvokeModel",
            "bedrock:InvokeModelWithResponseStream",
          ],
          resources: [
            "arn:aws:bedrock:us-east-1::foundation-model/amazon.nova-lite-v1:0",
            "arn:aws:bedrock:us-east-1::foundation-model/amazon.nova-pro-v1:0",
          ],
        },
      ],
    });

    return { apiUrl: api.url };
  },
});
